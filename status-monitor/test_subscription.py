import base64,importlib.util,json,pathlib,threading,unittest,http.server
spec=importlib.util.spec_from_file_location('sub_import',pathlib.Path(__file__).with_name('subscription.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
LINK='vless://dummy@node.example:443?type=tcp#DE'
class ImportTests(unittest.TestCase):
 def test_raw_and_dedup(self):
  self.assertEqual(m.targets(LINK+'\n'+LINK+'\ntrojan://dummy@other.example:8443'),[{'host':'node.example','port':443,'country':''},{'host':'other.example','port':8443,'country':''}])
 def test_base64(self):self.assertEqual(m.targets(base64.b64encode(LINK.encode()).decode())[0]['port'],443)
 def test_vmess_and_ipv6(self):
  vm='vmess://'+base64.b64encode(json.dumps({'add':'vm.example','port':'80','net':'ws'}).encode()).decode()
  self.assertEqual(m.targets(vm+'\nvless://x@[2001:db8::1]:443')[1]['host'],'2001:db8::1')
 def test_shadowsocks_legacy(self):
  uri='ss://'+base64.b64encode(b'aes-256-gcm:dummy@ss.example:443').decode()
  self.assertEqual(m.targets(uri)[0]['host'],'ss.example')
 def test_rendered_ghost_template(self):self.assertEqual(m.targets('<html><script>const RAW={links: `'+LINK+'`};</script></html>')[0]['host'],'node.example')
 def test_invalid_and_non_tcp(self):
  for text in ['<html>Login</html>','hysteria2://x@example.com:443',LINK.replace('type=tcp','type=quic'),'vless://x@node.example:99999']:
   with self.assertRaises(ValueError):m.targets(text)
 def test_bounds(self):
  with self.assertRaises(ValueError):m.targets('\n'.join('vless://x@n'+str(i)+'.example:443' for i in range(65)))
 def test_local_http_fetch(self):
  class Handler(http.server.BaseHTTPRequestHandler):
   def do_GET(self):
    body=base64.b64encode(LINK.encode());self.send_response(200);self.end_headers();self.wfile.write(body)
   def log_message(self,*a):pass
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:self.assertEqual(m.fetch('http://127.0.0.1:'+str(server.server_port)+'/private-sub')[0]['host'],'node.example')
  finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':unittest.main()
