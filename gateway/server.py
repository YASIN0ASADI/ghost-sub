#!/usr/bin/env python3
"""Fixed loopback subscription gateway + public monitor feed; no arbitrary proxy URL."""
import argparse,http.server,json,re,threading,urllib.parse,urllib.request,urllib.error
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
   if not monitor and not path.startswith(c['path_prefix']):self.reply(404,b'Not found');return
   if monitor:
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
    if monitor:
     data=json.loads(body)
     if data.get('schema')!=1 or not isinstance(data.get('nodes'),dict):raise ValueError('Invalid monitor feed')
     kind='application/json; charset=utf-8'
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
 def __init__(self,*args,**kwargs):self.slots=threading.BoundedSemaphore(32);super().__init__(*args,**kwargs)
 def get_request(self):sock,address=super().get_request();sock.settimeout(12);return sock,address
 def process_request(self,request,address):
  if not self.slots.acquire(False):
   try:request.sendall(b'HTTP/1.0 503 Busy\r\nContent-Length: 0\r\n\r\n')
   finally:self.shutdown_request(request)
   return
  try:super().process_request(request,address)
  except BaseException:self.slots.release();raise
 def process_request_thread(self,request,address):
  try:super().process_request_thread(request,address)
  finally:self.slots.release()
 def handle_error(self,*a):pass

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',default='/etc/ghost-gateway/config.json');a=p.parse_args();c=config(a.config)
 with Server(('0.0.0.0',c['listen_port']),handler(c)) as server:server.serve_forever()
if __name__=='__main__':main()
