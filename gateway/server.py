#!/usr/bin/env python3
"""Fixed loopback subscription gateway + public monitor feed; no arbitrary proxy URL."""
import argparse,http.server,http.client,json,re,threading,urllib.parse,urllib.request,urllib.error,ssl,socket,subprocess,ipaddress,os,tempfile,shutil
from pathlib import Path
LIMIT=4*1024*1024
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None

def config(path):
 c=json.loads(Path(path).read_text())
 for key in ['listen_port','upstream_port']:
  if not isinstance(c.get(key),int) or isinstance(c[key],bool) or not (1024 if key=='listen_port' else 1)<=c[key]<=65535:raise ValueError('Invalid public/upstream port')
 if c['listen_port'] in (c['upstream_port'],19191):raise ValueError('Gateway needs its own unused port')
 prefix=c.get('path_prefix','')
 if not re.fullmatch(r'/[A-Za-z0-9_/-]+/',prefix) or '..' in prefix or '//' in prefix:raise ValueError('Use the subscription path prefix, e.g. /sub/')
 if c.get('status_only'):
  origin=urllib.parse.urlsplit(c.get('allowed_origin',''))
  if origin.scheme not in ('http','https') or not origin.hostname or origin.path or origin.query or origin.fragment or origin.username or origin.password:raise ValueError('Expected exact HTTP/HTTPS subscription origin')
  if origin.scheme=='https' and not (c.get('tls_cert') and c.get('tls_key')):raise ValueError('HTTPS origin requires TLS certificate and key')
  if origin.scheme=='http' and (c.get('tls_cert') or c.get('tls_key')):raise ValueError('HTTP origin must use HTTP data')
 if c.get('tls_cert') or c.get('tls_key'):
  if not c.get('status_only'):raise ValueError('TLS is supported for data-only mode')
  for k in ('tls_cert','tls_key'):
   if not isinstance(c.get(k),str) or not Path(c[k]).is_absolute():raise ValueError('TLS paths must be absolute')
  tls_context(c)
 return c

def tls_context(c):
 if not c.get('tls_cert'):return None
 ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.minimum_version=ssl.TLSVersion.TLSv1_2
 ctx.load_cert_chain(c['tls_cert'],c['tls_key'],password=lambda:'')
 return ctx

def validate_certificate(c):
 # Existing certificate only; never issue or accept an insecure browser exception.
 host=urllib.parse.urlsplit(c['allowed_origin']).hostname
 try:ipaddress.ip_address(host);flag='-verify_ip'
 except ValueError:flag='-verify_hostname'
 commands=[['openssl','x509','-in',c['tls_cert'],'-noout','-checkend','86400'],
           ['openssl','verify','-partial_chain','-trusted',c['tls_cert'],'-purpose','sslserver',flag,host,c['tls_cert']]]
 for command in commands:
  result=subprocess.run(command,capture_output=True,timeout=10)
  if result.returncode:raise ValueError('Certificate must match subscription host and remain valid for at least 24 hours')
 tls_context(c)

def local_get(c,path,context=None):
 # Connect locally, but use the actual subscription hostname for verified TLS.
 host=urllib.parse.urlsplit(c.get('allowed_origin','http://localhost')).hostname
 with socket.create_connection(('127.0.0.1',c['listen_port']),timeout=2) as raw:
  wire=raw
  if c.get('tls_cert'):wire=(context or ssl.create_default_context()).wrap_socket(raw,server_hostname=host)
  try:
   wire.sendall(('GET '+path+' HTTP/1.1\r\nHost: '+host+'\r\nConnection: close\r\n\r\n').encode('ascii'))
   response=http.client.HTTPResponse(wire);response.begin();body=response.read(100001)
   if len(body)>100000:raise ValueError('Oversized local feed')
   return response.status,body
  finally:
   if wire is not raw:wire.close()

def install_tls_config(c,root,gid,uid=0):
 root=Path(root);c=dict(c)
 destination=root/'config.json'
 if destination.is_symlink():raise ValueError('Config symlink refused')
 if c.get('tls_cert'):
  folder=Path(tempfile.mkdtemp(prefix='tls-',dir=root))
  os.chown(folder,uid,gid);os.chmod(folder,0o750)
  for field,name in [('tls_cert','fullchain.pem'),('tls_key','privkey.pem')]:
   target=folder/name;shutil.copyfile(c[field],target)
   os.chown(target,uid,gid);os.chmod(target,0o640);c[field]=str(target)
 fd,tmp=tempfile.mkstemp(prefix='.config-',dir=root)
 try:
  with os.fdopen(fd,'w') as f:json.dump(c,f)
  os.chown(tmp,uid,gid);os.chmod(tmp,0o640);os.replace(tmp,destination)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
 return c

def patch_html(body):
 text=body.decode('utf-8')
 text,count=re.subn(r'(<meta\s+name="ghost-status-feed"\s+content=")[^"]*("\s*>)',lambda m:m[1]+'/ghost-status.json'+m[2],text,count=1)
 if count!=1:raise ValueError('Install the current Ghost Sub template before using this gateway')
 return text.encode()

def handler(c):
 class Handler(http.server.BaseHTTPRequestHandler):
  def reply(self,code,body,content='text/plain; charset=utf-8',extra=()):
   self.send_response(code)
   for name,value in extra:self.send_header(name,value)
   self.send_header('Content-Type',content);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.end_headers()
   if self.command!='HEAD':self.wfile.write(body)
  def do_HEAD(self):self.do_GET()
  def do_GET(self):
   parsed=urllib.parse.urlsplit(self.path);path=urllib.parse.unquote(parsed.path)
   if parsed.scheme or parsed.netloc or '..' in path.split('/') or '\\' in path or '//' in path:
    self.reply(404,b'Not found');return
   monitor=path=='/ghost-status.json'
   usage=bool(c.get('history_enabled')) and bool(re.fullmatch(r'/ghost-usage/[A-Za-z0-9_-]{8,128}',path)) and not parsed.query
   if not monitor and not usage and (c.get('status_only') or not path.startswith(c['path_prefix'])):self.reply(404,b'Not found');return
   if usage:
    url='http://127.0.0.1:19192/history/'+path.rsplit('/',1)[1];headers={}
   elif monitor:
    url='http://127.0.0.1:19191/status.json';headers={}
   else:
    authority=self.headers.get('Host','')
    if not re.fullmatch(r'[A-Za-z0-9.\-\[\]:]+',authority):self.reply(400,b'Invalid host');return
    url='http://127.0.0.1:'+str(c['upstream_port'])+self.path
    headers={'Host':authority,'User-Agent':self.headers.get('User-Agent','Ghost-Sub-Gateway'),'Accept':self.headers.get('Accept','*/*'),'Accept-Encoding':'identity'}
   try:
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect()).open(req,timeout=10) as response:
     body=response.read(LIMIT+1);kind=response.headers.get('Content-Type','application/octet-stream')
     extra=[(key,value) for key,value in response.headers.items() if key.lower() in ('subscription-userinfo','profile-update-interval','profile-title')]
     if len(body)>LIMIT or response.headers.get('Content-Encoding','identity')!='identity':raise ValueError('Unsupported response')
    if monitor or usage:
     data=json.loads(body)
     if data.get('schema')!=1:raise ValueError('Invalid feed')
     if monitor and not isinstance(data.get('nodes'),dict):raise ValueError('Invalid monitor feed')
     if usage and (data.get('source')!='sampled_3xui_counters' or not isinstance(data.get('points'),list)):raise ValueError('Invalid history feed')
     kind='application/json; charset=utf-8'
     extra=[]
     if c.get('allowed_origin') and self.headers.get('Origin')==c['allowed_origin']:
      extra=[('Access-Control-Allow-Origin',c['allowed_origin']),('Vary','Origin')]
    elif 'text/html' in kind:
     body=patch_html(body);kind='text/html; charset=utf-8'
    self.reply(200,body,kind,extra)
   except urllib.error.HTTPError as error:
    # Upstream response bodies/redirects may contain private links; do not export them.
    self.reply(error.code if error.code in (401,403,404,429) else 502,b'Upstream unavailable')
   except Exception:self.reply(502,b'Gateway upstream unavailable; check local services/template')
  def log_message(self,*a):pass
 return Handler

class Server(http.server.ThreadingHTTPServer):
 daemon_threads=True
 def __init__(self,*args,tls=None,**kwargs):self.tls=tls;self.slots=threading.BoundedSemaphore(32);super().__init__(*args,**kwargs)
 def get_request(self):sock,address=super().get_request();sock.settimeout(12);return sock,address
 def process_request(self,request,address):
  if not self.slots.acquire(False):
   try:request.sendall(b'HTTP/1.0 503 Busy\r\nContent-Length: 0\r\n\r\n')
   finally:self.shutdown_request(request)
   return
  try:super().process_request(request,address)
  except BaseException:self.slots.release();raise
 def process_request_thread(self,request,address):
  try:
   if self.tls:
    request=self.tls.wrap_socket(request,server_side=True,do_handshake_on_connect=False)
    request.do_handshake()
   super().process_request_thread(request,address)
  except Exception:self.shutdown_request(request)
  finally:self.slots.release()
 def handle_error(self,*a):pass

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',default='/etc/ghost-gateway/config.json');a=p.parse_args();c=config(a.config)
 with Server(('0.0.0.0',c['listen_port']),handler(c),tls=tls_context(c)) as server:server.serve_forever()
if __name__=='__main__':main()
