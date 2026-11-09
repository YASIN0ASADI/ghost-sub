import http.server,importlib.util,json,pathlib,tempfile,threading,time,unittest,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parent.parent
for name,file in [('gateway',ROOT/'gateway/server.py'),('history',ROOT/'traffic-history/history.py')]:
 spec=importlib.util.spec_from_file_location(name,file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);globals()[name]=module
A='abcdefghijklmnop';B='qrstuvwxyz123456'
class UsageRouteTests(unittest.TestCase):
 def test_real_history_isolation_and_cors_through_gateway(self):
  with tempfile.TemporaryDirectory() as d:
   dbpath=pathlib.Path(d)/'history.sqlite3';db=history.database(dbpath);now=time.time()
   def record(token,value):return {'sub':token,'stream':'client'+token,'generation':'same','used':value,'reset':0}
   history.ingest(db,[record(A,100),record(B,1000)],now-900,900)
   history.ingest(db,[record(A,600),record(B,2200)],now,900);db.close()
   class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
     reader=history.database(dbpath)
     try:result=history.history(reader,self.path.removeprefix('/history/'),time.time(),900)
     finally:reader.close()
     if result is None:self.send_error(404);return
     self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
    def log_message(self,*a):pass
   try:backend=http.server.ThreadingHTTPServer(('127.0.0.1',19192),Handler)
   except OSError:self.skipTest('History test port occupied')
   cfg={'status_only':True,'history_enabled':True,'allowed_origin':'http://original.example:2096','path_prefix':'/sub/','upstream_port':2096}
   server=gateway.Server(('127.0.0.1',0),gateway.handler(cfg));threads=[]
   try:
    for item in [backend,server]:
     t=threading.Thread(target=item.serve_forever,daemon=True);t.start();threads.append(t)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
    for token,expected in [(A,500),(B,1200)]:
     req=urllib.request.Request(base+'/ghost-usage/'+token,headers={'Origin':cfg['allowed_origin']})
     with opener.open(req) as r:
      self.assertEqual(r.headers['Access-Control-Allow-Origin'],cfg['allowed_origin'])
      data=r.read().decode();self.assertNotIn(A,data);self.assertNotIn(B,data)
      self.assertEqual(json.loads(data)['points'][-1]['used'],expected)
    with opener.open(urllib.request.Request(base+'/ghost-usage/'+A,headers={'Origin':'http://foreign.example'})) as r:self.assertIsNone(r.headers.get('Access-Control-Allow-Origin'))
    for path in ['/ghost-usage/','/ghost-usage/unknown12345678','/ghost-usage/'+A+'?anything=1','/history/'+A,'/sub/'+A]:
     with self.assertRaises(urllib.error.HTTPError) as ctx:opener.open(base+path)
     self.assertEqual(ctx.exception.code,404)
    cfg['history_enabled']=False
    with self.assertRaises(urllib.error.HTTPError):opener.open(base+'/ghost-usage/'+A)
   finally:
    for item in [server,backend]:item.shutdown();item.server_close()
    for t in threads:t.join()
if __name__=='__main__':unittest.main()
