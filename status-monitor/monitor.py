#!/usr/bin/env python3
"""Fixed-target TCP reachability samples; no panel credentials, OS uptime or proxy health claims."""
import argparse, concurrent.futures, hashlib, http.server, ipaddress, json, os, re, socket, sqlite3, tempfile, threading, time
from pathlib import Path


def endpoint_id(host, port):
    return hashlib.sha256((host.lower().rstrip('.')+':'+str(port)).encode()).hexdigest()[:24]


def config(path):
    c=json.loads(Path(path).read_text())
    c.setdefault('interval_seconds',60);c.setdefault('timeout_seconds',3)
    c.setdefault('listen_port',19191);c.setdefault('probe_label','Monitoring server')
    if not 30<=c['interval_seconds']<=3600 or not 0.1<=c['timeout_seconds']<=10:
        raise ValueError('Invalid interval/timeout')
    if not 1024<=c['listen_port']<=65535:raise ValueError('Invalid listen port')
    if not isinstance(c.get('targets'),list) or not 1<=len(c['targets'])<=64:raise ValueError('Configure 1–64 targets')
    if not isinstance(c['probe_label'],str) or len(c['probe_label'])>80:raise ValueError('Invalid probe label')
    seen=set()
    for t in c['targets']:
        h=t.get('host','');p=t.get('port')
        if not isinstance(h,str) or not h or len(h)>253 or not re.fullmatch(r'[a-zA-Z0-9._:\-]+',h):raise ValueError('Invalid target host')
        if not isinstance(p,int) or isinstance(p,bool) or not 1<=p<=65535:raise ValueError('Invalid target port')
        try:
            a=ipaddress.ip_address(h)
            if a.is_unspecified or a.is_multicast:raise ValueError('Unicast target required')
        except ValueError:
            if ':' in h or re.fullmatch(r'[0-9.]+',h):raise ValueError('Invalid target IP')
        key=endpoint_id(h,p)
        if key in seen:raise ValueError('Duplicate target')
        seen.add(key);t['id']=key
        country=t.get('country','')
        if not isinstance(country,str) or (country and not re.fullmatch('[A-Z]{2}',country)):raise ValueError('Country must be an explicit ISO2 code')
    return c


def open_db(path):
    db=sqlite3.connect(path)
    db.execute('CREATE TABLE IF NOT EXISTS samples (node TEXT NOT NULL, t REAL NOT NULL, ok INTEGER NOT NULL, latency REAL, PRIMARY KEY(node,t))')
    db.execute('CREATE INDEX IF NOT EXISTS sample_time ON samples(t)')
    db.commit();return db


def check(target,timeout):
    start=time.monotonic()
    try:
        with socket.create_connection((target['host'],target['port']),timeout=timeout):
            return True,round((time.monotonic()-start)*1000,1)
    except OSError:return False,None


def summarize(rows,now,interval):
    rows=[r for r in rows if now-86400<=r[0]<=now]
    if not rows:return dict(state='unknown',last_checked=None,samples=0,successful_samples=0,availability_pct=None,observed_seconds=0,tcp_connect_ms=None,history=[None]*24)
    rows.sort();recent=rows[-3:];last=rows[-1]
    if now-last[0]>max(180,interval*3):state='unknown'
    elif len(recent)>=3 and not any(r[1] for r in recent):state='down'
    elif not all(r[1] for r in recent):state='unstable'
    else:state='up'
    # Discrete sample ratio; missing periods are never counted as successes.
    ok=sum(bool(r[1]) for r in rows)
    history=[]
    for hour in range(24):
        a=now-(24-hour)*3600;b=a+3600
        bucket=[r for r in rows if a<r[0]<=b]
        history.append(None if not bucket else round(100*sum(bool(r[1]) for r in bucket)/len(bucket),1))
    return dict(state=state,last_checked=int(last[0]),samples=len(rows),successful_samples=ok,availability_pct=round(100*ok/len(rows),2),observed_seconds=int(max(0,last[0]-rows[0][0])),tcp_connect_ms=last[2] if last[1] else None,history=history)


def snapshot(db,c,now=None):
    now=time.time() if now is None else now
    nodes={}
    for t in c['targets']:
        rows=db.execute('SELECT t,ok,latency FROM samples WHERE node=? AND t>=? ORDER BY t',(t['id'],now-86400)).fetchall()
        nodes[t['id']]=dict(summarize(rows,now,c['interval_seconds']),country=t.get('country',''))
    return dict(schema=1,generated_at=int(now),interval_seconds=c['interval_seconds'],probe_label=c['probe_label'],measurement='tcp_connect_samples',nodes=nodes)


def cycle(db,c):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs=[pool.submit(check,t,c['timeout_seconds']) for t in c['targets']]
        for target,job in zip(c['targets'],jobs):
            ok,latency=job.result()
            db.execute('INSERT INTO samples VALUES (?,?,?,?)',(target['id'],time.time(),int(ok),latency))
    db.execute('DELETE FROM samples WHERE t<?',(time.time()-86400*2,));db.commit()
    return snapshot(db,c)


def atomic_json(path,data):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.ghost-status-',dir=p.parent)
    try:
        with os.fdopen(fd,'w') as f:json.dump(data,f,ensure_ascii=False);f.flush();os.fsync(f.fileno())
        os.replace(temp,p)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',required=True);p.add_argument('--state-dir',default='/var/lib/ghost-status')
    p.add_argument('--once',action='store_true');p.add_argument('--output',help='Optional JSON export; it must be served explicitly by your web server')
    a=p.parse_args();c=config(a.config);state=Path(a.state_dir);state.mkdir(parents=True,exist_ok=True)
    db=open_db(str(state/'samples.sqlite3'));lock=threading.Lock();live={'data':snapshot(db,c)}
    if a.once:
        data=cycle(db,c)
        if a.output:atomic_json(a.output,data)
        else:print(json.dumps(data,ensure_ascii=False,indent=2))
        return
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path!='/status.json':self.send_error(404);return
            with lock:body=json.dumps(live['data'],ensure_ascii=False).encode()
            self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def log_message(self,*args):pass
    # No request can add targets or trigger scans. Fixed loopback binding.
    server=http.server.ThreadingHTTPServer(('127.0.0.1',c['listen_port']),Handler)
    server.daemon_threads=True
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        while True:
            started=time.monotonic();data=cycle(db,c)
            with lock:live['data']=data
            if a.output:atomic_json(a.output,data)
            time.sleep(max(0,c['interval_seconds']-(time.monotonic()-started)))
    except KeyboardInterrupt:pass
    finally:server.shutdown();db.close()


if __name__=='__main__':main()
