"""Real TLS loopback tests; certificates are generated fixtures, never user keys."""
import os
import http.server,importlib.util,json,pathlib,ssl,socket,subprocess,tempfile,threading,unittest,urllib.request
spec=importlib.util.spec_from_file_location('tls_gateway',pathlib.Path(__file__).with_name('server.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TLSTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.root=pathlib.Path(cls.tmp.name)
  cls.cert=cls.root/'cert.pem';cls.key=cls.root/'key.pem'
  subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','2','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost','-keyout',str(cls.key),'-out',str(cls.cert)],check=True,capture_output=True)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def cfg(self):return dict(listen_port=18090,upstream_port=443,path_prefix='/sub/',status_only=True,allowed_origin='https://localhost:2096',tls_cert=str(self.cert),tls_key=str(self.key),history_enabled=True)
 def test_config_and_certificate_validation(self):
  c=self.cfg();m.validate_certificate(c)
  p=self.root/'config.json';p.write_text(json.dumps(c));m.config(p)
  for change in [dict(tls_key=''),dict(tls_cert=''),dict(status_only=False),dict(allowed_origin='http://localhost:2096')]:
   p.write_text(json.dumps({**c,**change}))
   with self.assertRaises((ValueError,ssl.SSLError,FileNotFoundError)):m.config(p)
  with self.assertRaises(ValueError):m.validate_certificate({**c,'allowed_origin':'https://wrong.invalid'})
 def test_installed_private_copies_and_rotation_preserve_previous_config(self):
  with tempfile.TemporaryDirectory() as d:
   c=self.cfg();first=m.install_tls_config(c,d,os.getgid(),os.getuid())
   second=m.install_tls_config(c,d,os.getgid(),os.getuid())
   self.assertNotEqual(first['tls_key'],second['tls_key'])
   self.assertEqual(c['tls_key'],str(self.key))
   for field in ('tls_cert','tls_key'):
    p=pathlib.Path(first[field]);self.assertTrue(p.is_file());self.assertEqual(p.stat().st_mode&0o777,0o640)
    self.assertEqual(p.parent.stat().st_mode&0o777,0o750)
   self.assertEqual((pathlib.Path(d)/'config.json').stat().st_mode&0o777,0o640)
   # Rollback points at the untouched prior certificate/key files.
   m.tls_context(first)
 def test_verified_tls_cors_history_and_no_plaintext_downgrade(self):
  class Backend(http.server.BaseHTTPRequestHandler):
   def do_GET(self):
    if self.path.startswith('/history/'):
     data={'schema':1,'source':'sampled_3xui_counters','points':[{'t':1,'used':55}]}
    else:data={'schema':1,'nodes':{}}
    self.send_response(200);self.end_headers();self.wfile.write(json.dumps(data).encode())
   def log_message(self,*args):pass
  servers=[];threads=[];slow=None
  try:
   try:
    for port in (19191,19192):servers.append(http.server.ThreadingHTTPServer(('127.0.0.1',port),Backend))
   except OSError:self.skipTest('Loopback fixture port occupied')
   c=self.cfg();server=m.Server(('127.0.0.1',0),m.handler(c),tls=m.tls_context(c));servers.append(server);c['listen_port']=server.server_port
   for s in servers:
    t=threading.Thread(target=s.serve_forever,daemon=True);t.start();threads.append(t)
   trusted=ssl.create_default_context(cafile=str(self.cert))
   code,body=m.local_get(c,'/ghost-status.json',context=trusted)
   self.assertEqual(code,200);self.assertEqual(json.loads(body)['schema'],1)
   with self.assertRaises(ssl.SSLCertVerificationError):m.local_get(c,'/ghost-status.json')
   with self.assertRaises(ssl.SSLCertVerificationError):m.local_get({**c,'allowed_origin':'https://wrong.invalid'},'/ghost-status.json',context=trusted)
   slow=socket.create_connection(('127.0.0.1',server.server_port))
   self.assertEqual(m.local_get(c,'/ghost-status.json',context=trusted)[0],200)
   opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=trusted))
   base='https://localhost:'+str(server.server_port)
   for path in ('/ghost-status.json','/ghost-usage/abcdefghijklmnop'):
    with opener.open(urllib.request.Request(base+path,headers={'Origin':c['allowed_origin']}),timeout=3) as r:
     self.assertEqual(r.headers['Access-Control-Allow-Origin'],c['allowed_origin'])
     self.assertNotIn('abcdefghijklmnop',r.read().decode())
    with opener.open(urllib.request.Request(base+path,headers={'Origin':'https://foreign.invalid'}),timeout=3) as r:self.assertIsNone(r.headers.get('Access-Control-Allow-Origin'))
   self.assertEqual(m.local_get(c,'/sub/abcdefghijklmnop',context=trusted)[0],404)
   with self.assertRaises(Exception):urllib.request.urlopen('http://127.0.0.1:'+str(server.server_port)+'/ghost-status.json',timeout=2)
  finally:
   if slow:slow.close()
   for s in servers:s.shutdown();s.server_close()
   for t in threads:t.join()
if __name__=='__main__':unittest.main()
