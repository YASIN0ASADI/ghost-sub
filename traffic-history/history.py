#!/usr/bin/env python3
"""Optional 3X-UI v2/v3 sampled usage history. Fixed panel, private credentials, own-subscription-only reads."""
import argparse, getpass, hashlib, http.cookiejar, http.server, ipaddress, json, os, re, socket, sqlite3, ssl, threading, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
TOKEN=re.compile(r'^[A-Za-z0-9_-]{8,128}$')
class Unsupported(Exception):pass
class Authentication(Exception):pass
class Unavailable(Exception):pass

def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or value<0 or int(value)!=value:raise Unsupported('Invalid traffic counter')
    return int(value)

def obj(response):
    if not isinstance(response,dict) or response.get('success') is not True:raise Unsupported('Unsupported API response')
    value=response.get('obj')
    if not isinstance(value,list):raise Unsupported('Expected a complete client/inbound list')
    return value

def normalize_v3(response):
    out=[];seen=set()
    for record in obj(response):
        if not isinstance(record,dict):raise Unsupported('Invalid client shape')
        client=record.get('client',record);traffic=record.get('traffic')
        if not isinstance(client,dict):raise Unsupported('Invalid client shape')
        if traffic is None:continue
        if not isinstance(traffic,dict) or 'up' not in traffic or 'down' not in traffic:raise Unsupported('Missing per-client counters')
        sub=client.get('subId','');email=client.get('email','')
        if not isinstance(sub,str) or not TOKEN.fullmatch(sub):continue
        identity=str(client.get('id') or email)
        if not identity:raise Unsupported('Missing client identity')
        key=(sub,identity)
        if key in seen:raise Unsupported('Duplicate client record')
        seen.add(key)
        out.append(dict(sub=sub,stream='v3:'+identity,used=number(traffic['up'])+number(traffic['down']),reset=traffic.get('resetCount'),generation=str(client.get('uuid') or client.get('password') or '')))
    return out

def normalize_v2(response):
    out=[];seen=set()
    for inbound in obj(response):
        if not isinstance(inbound,dict):raise Unsupported('Invalid inbound shape')
        settings=inbound.get('settings')
        if isinstance(settings,str):
            try:settings=json.loads(settings)
            except ValueError:raise Unsupported('Invalid settings JSON')
        clients={c.get('email'):c for c in (settings or {}).get('clients',[]) if isinstance(c,dict) and c.get('email')}
        stats=inbound.get('clientStats')
        if stats is None:continue
        if not isinstance(stats,list):raise Unsupported('Invalid clientStats')
        for row in stats:
            if not isinstance(row,dict):raise Unsupported('Invalid traffic row')
            client=clients.get(row.get('email'),{});sub=row.get('subId') or client.get('subId')
            if not isinstance(sub,str) or not TOKEN.fullmatch(sub):continue
            if 'up' not in row or 'down' not in row:raise Unsupported('Missing counters')
            # Traffic record ID is globally unique where supplied; otherwise
            # scope legacy records by inbound and email (do not double-count repeated IDs).
            stream='v2:'+str(row['id']) if row.get('id') else 'v2:'+str(inbound.get('id'))+':'+str(row.get('email'))
            key=(sub,stream)
            if key in seen:continue
            seen.add(key)
            out.append(dict(sub=sub,stream=stream,used=number(row['up'])+number(row['down']),reset=row.get('resetCount'),generation=str(row.get('uuid') or client.get('id') or client.get('password') or '')))
    return out

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

class API:
    def __init__(self,c):
        self.c=c;self.base=c['panel_url'].rstrip('/')+'/'
        self.opener=urllib.request.build_opener(NoRedirect(),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),urllib.request.HTTPSHandler(context=ssl.create_default_context(cafile=c.get('ca_file') or None)))
    def request(self,path,data=None):
        headers={'Accept':'application/json'}
        if self.c.get('api_token'):headers['Authorization']='Bearer '+self.c['api_token']
        if data is not None:headers['Content-Type']='application/x-www-form-urlencoded'
        req=urllib.request.Request(self.base+path,urllib.parse.urlencode(data).encode() if data is not None else None,headers)
        try:
            with self.opener.open(req,timeout=15) as response:
                raw=response.read(16*1024*1024+1)
        except urllib.error.HTTPError as e:
            if e.code in (401,403):raise Authentication('Panel authentication/permission failed') from None
            if e.code in (404,405):raise Unsupported('API route not available') from None
            raise Unavailable('Panel HTTP error') from None
        except (OSError,urllib.error.URLError):raise Unavailable('Panel request unavailable') from None
        if len(raw)>16*1024*1024:raise Unsupported('API response too large')
        try:return json.loads(raw)
        except ValueError:raise Unsupported('Panel did not return JSON') from None
    def collect(self):
        if not self.c.get('api_token'):
            result=self.request('login',{'username':self.c['username'],'password':self.c['password']})
            if result.get('success') is not True:raise Authentication('Panel login failed')
        mode=self.c.get('api_mode','auto')
        if mode=='auto':mode=getattr(self,'selected','auto')
        if mode in ('auto','v3'):
            try:
                rows=normalize_v3(self.request('panel/api/clients/list'));self.selected='v3';return rows,'v3'
            except Unsupported:
                if mode=='v3':raise
        rows=normalize_v2(self.request('panel/api/inbounds/list'));self.selected='v2';return rows,'v2'

def load_config(path):
    c=json.loads(Path(path).read_text());u=urllib.parse.urlsplit(c.get('panel_url',''))
    if not u.hostname or u.username or u.password or u.query or u.fragment:raise ValueError('Invalid panel URL')
    if u.scheme!='https':
        try:local=ipaddress.ip_address(u.hostname).is_loopback
        except ValueError:local=False
        if u.scheme!='http' or not local:raise ValueError('Use HTTPS or a literal loopback HTTP panel URL')
    if not c.get('api_token') and not (c.get('username') and c.get('password')):raise ValueError('Configure private API token or login credentials')
    if c.get('api_mode','auto') not in ('auto','v2','v3'):raise ValueError('Invalid API mode')
    c.setdefault('interval_seconds',900);c.setdefault('listen_port',19192)
    if not 60<=c['interval_seconds']<=3600 or not 1024<=c['listen_port']<=65535:raise ValueError('Invalid interval/port')
    return c

def hash_id(text):return hashlib.sha256(text.encode()).hexdigest()

def database(path):
    db=sqlite3.connect(path)
    db.executescript('CREATE TABLE IF NOT EXISTS counters(sub TEXT,stream TEXT,last INTEGER,reset TEXT,generation TEXT,t REAL,PRIMARY KEY(sub,stream)); CREATE TABLE IF NOT EXISTS totals(sub TEXT PRIMARY KEY,used INTEGER,updated REAL); CREATE TABLE IF NOT EXISTS points(sub TEXT,t REAL,used INTEGER,gap INTEGER,PRIMARY KEY(sub,t)); CREATE INDEX IF NOT EXISTS points_time ON points(t);')
    db.execute('CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY,value TEXT)')
    return db

def ingest(db,records,now,interval):
    by_sub={}
    for r in records:by_sub.setdefault(hash_id(r['sub']),[]).append(r)
    with db:
        # A successfully fetched complete list revokes histories for removed subscriptions.
        db.execute('UPDATE totals SET updated=0')
        for sub,rows in by_sub.items():
            total=db.execute('SELECT used FROM totals WHERE sub=?',(sub,)).fetchone();used=total[0] if total else 0;gap=0
            for r in rows:
                stream=hash_id(r['stream']);generation=hash_id(r['generation']);reset=json.dumps(r['reset'])
                previous=db.execute('SELECT last,reset,generation,t FROM counters WHERE sub=? AND stream=?',(sub,stream)).fetchone()
                if not previous and total:gap=1
                if previous:
                    old,old_reset,old_generation,t=previous
                    if generation!=old_generation:gap=1  # new account generation: establish a baseline
                    elif t < now-interval*3:gap=1  # missed collection: do not attribute unknown interval
                    elif r['used']<old or (r['reset'] is not None and old_reset!=reset):used+=r['used'];gap=1
                    else:used+=r['used']-old
                db.execute('INSERT OR REPLACE INTO counters VALUES (?,?,?,?,?,?)',(sub,stream,r['used'],reset,generation,now))
            db.execute('INSERT OR REPLACE INTO totals VALUES (?,?,?)',(sub,used,now))
            db.execute('INSERT OR REPLACE INTO points VALUES (?,?,?,?)',(sub,now,used,gap))
        db.execute('DELETE FROM points WHERE t<?',(now-60*86400,))
    return len(by_sub)

def history(db,token,now,interval):
    if not TOKEN.fullmatch(token):return None
    sub=hash_id(token);row=db.execute('SELECT updated FROM totals WHERE sub=?',(sub,)).fetchone()
    if not row or row[0]<=0 or now-row[0]>max(3600,interval*3):return None
    rows=db.execute('SELECT t,used,gap FROM points WHERE sub=? AND t>=? ORDER BY t',(sub,now-31*86400)).fetchall()
    return {'schema':1,'source':'sampled_3xui_counters','updated_at':int(row[0]),'points':[{'t':int(t*1000),'used':used,'gap':bool(gap)} for t,used,gap in rows]}

def configure(path):
    p=Path(path)
    if p.exists():print('Existing config retained. Edit it privately to change credentials.');return
    c={'panel_url':input('Panel base URL (include custom base path): ').strip(),'api_mode':input('API mode [auto/v2/v3; default auto]: ').strip() or 'auto'}
    token=getpass.getpass('Scoped read API token (Enter for session login): ')
    if token:c['api_token']=token
    else:c.update(username=input('Panel username: ').strip(),password=getpass.getpass('Panel password: '))
    c.update(interval_seconds=900,listen_port=19192)
    p.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(c,f,indent=2)
    try:load_config(p)
    except Exception:p.unlink();raise
    print('Private configuration saved; no API requests or service start performed.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True);p.add_argument('--state-dir',default='/var/lib/ghost-history');p.add_argument('--once',action='store_true');p.add_argument('--configure',action='store_true');a=p.parse_args()
    if a.configure:configure(a.config);return
    c=load_config(a.config);state=Path(a.state_dir);state.mkdir(parents=True,exist_ok=True);db=database(state/'history.sqlite3');api=API(c)
    pinned=db.execute("SELECT value FROM meta WHERE key='adapter'").fetchone()
    if c.get('api_mode','auto')=='auto' and pinned and pinned[0] in ('v2','v3'):api.selected=pinned[0]
    def collect_once():
        records,mode=api.collect();count=ingest(db,records,time.time(),c['interval_seconds'])
        with db:db.execute("INSERT OR REPLACE INTO meta VALUES ('adapter',?)",(mode,))
        return count,mode
    if a.once:
        count,mode=collect_once();print(json.dumps({'api_mode':mode,'subscriptions_sampled':count}));return
    lock=threading.Lock();budget={'second':0,'count':0}
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            # Loopback-only origin; publish through HTTPS proxy without logging subscription tokens.
            second=int(time.time())
            with lock:
                if budget['second']!=second:budget.update(second=second,count=0)
                budget['count']+=1
                if budget['count']>20:self.send_error(429);return
            prefix='/history/'
            token=self.path[len(prefix):] if self.path.startswith(prefix) else ''
            reader=database(state/'history.sqlite3')
            try:body=history(reader,token,time.time(),c['interval_seconds'])
            finally:reader.close()
            if body is None:self.send_error(404);return
            data=json.dumps(body).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',c['listen_port']),Handler);server.daemon_threads=True;threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        while True:
            started=time.monotonic()
            try:
                count,mode=collect_once();print(json.dumps({'api_mode':mode,'subscriptions_sampled':count}),flush=True)
            except (Unsupported,Authentication,Unavailable,ValueError):print('History collection unavailable; check API compatibility/auth privately. Existing page remains usable.',flush=True)
            time.sleep(max(0,c['interval_seconds']-(time.monotonic()-started)))
    except KeyboardInterrupt:pass
    finally:server.shutdown();db.close()
if __name__=='__main__':
    try:main()
    except (ValueError,Unsupported,Authentication,Unavailable):raise SystemExit('History configuration/API unavailable; credentials are not printed.')
