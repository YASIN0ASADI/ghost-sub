import http.server,importlib.util,json,pathlib,tempfile,threading,unittest,urllib.request,urllib.error
spec=importlib.util.spec_from_file_location('gateway',pathlib.Path(__file__).with_name('server.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class GatewayTests(unittest.TestCase):
 def test_html_feed_injection(self):
  source=b'<html><meta name="ghost-status-feed" content="https://old.example/status"></html>'
  self.assertIn(b'content="/ghost-status.json"',m.patch_html(source))
  with self.assertRaises(ValueError):m.patch_html(b'<html>old template</html>')
 def test_config_bounds(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'config.json'
   for value,ok in [({'listen_port':18090,'upstream_port':2096,'path_prefix':'/sub/'},True),({'listen_port':18090,'upstream_port':80,'path_prefix':'/sub/'},True),({'listen_port':19191,'upstream_port':2096,'path_prefix':'/sub/'},False),({'listen_port':18090,'upstream_port':2096,'path_prefix':'/'},False)]:
    p.write_text(json.dumps(value))
    if ok:m.config(p)
    else:
     with self.assertRaises(ValueError):m.config(p)
 def test_real_loopback_page_raw_feed_and_restrictions(self):
  seen=[]
  class Backend(http.server.BaseHTTPRequestHandler):
   def do_GET(self):
    seen.append((self.path,self.headers.get('Host'),self.headers.get('Cookie')))
    if self.path=='/sub/raw':body=b'dummy-base64';kind='text/plain'
    elif self.path=='/sub/redirect':self.send_response(302);self.send_header('Location','http://outside.invalid/private');self.end_headers();return
    else:body=b'<html><meta name="ghost-status-feed" content=""></html>';kind='text/html'
    self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Subscription-Userinfo','upload=1; download=2');self.end_headers();self.wfile.write(body)
   def log_message(self,*a):pass
  class Monitor(http.server.BaseHTTPRequestHandler):
   def do_GET(self):self.send_response(200);self.end_headers();self.wfile.write(b'{"schema":1,"nodes":{}}')
   def log_message(self,*a):pass
  servers=[];threads=[]
  try:
   try:monitor=http.server.ThreadingHTTPServer(('127.0.0.1',19191),Monitor)
   except OSError:self.skipTest('Local monitor port occupied')
   servers.append(monitor)
   backend=http.server.ThreadingHTTPServer(('127.0.0.1',0),Backend);servers.append(backend)
   gateway=m.Server(('127.0.0.1',0),m.handler({'upstream_port':backend.server_port,'path_prefix':'/sub/'}));servers.append(gateway)
   for server in servers:
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start();threads.append(t)
   opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));base='http://127.0.0.1:'+str(gateway.server_port)
   with opener.open(urllib.request.Request(base+'/sub/private',headers={'Cookie':'admin=private'})) as r:self.assertIn(b'/ghost-status.json',r.read())
   self.assertEqual(seen[-1],('/sub/private','127.0.0.1:'+str(gateway.server_port),None))
   with opener.open(base+'/sub/raw') as r:self.assertEqual(r.read(),b'dummy-base64');self.assertEqual(r.headers['Subscription-Userinfo'],'upload=1; download=2')
   with opener.open(base+'/ghost-status.json') as r:self.assertEqual(json.loads(r.read())['schema'],1)
   for path in ['/admin','/sub/../admin','/sub/redirect']:
    with self.assertRaises(urllib.error.HTTPError) as ctx:opener.open(base+path)
    self.assertIn(ctx.exception.code,[404,502])
  finally:
   for server in servers:server.shutdown();server.server_close()
   for t in threads:t.join()
if __name__=='__main__':unittest.main()
