import importlib.util,json,sqlite3,tempfile,unittest,urllib.error
from pathlib import Path
spec=importlib.util.spec_from_file_location('history',Path(__file__).with_name('history.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
SUB='abcdefghijklmnop';OTHER='qrstuvwxyz123456'
def record(used,reset=0,generation='uuid',sub=SUB):return dict(sub=sub,stream='client1',used=used,reset=reset,generation=generation)
class HistoryTests(unittest.TestCase):
 def setUp(self):self.db=m.database(':memory:')
 def tearDown(self):self.db.close()
 def test_v3_flat_and_wrapped(self):
  r={'email':'a','id':1,'subId':SUB,'uuid':'u','traffic':{'up':10,'down':20}}
  self.assertEqual(m.normalize_v3({'success':True,'obj':[r]})[0]['used'],30)
  self.assertEqual(m.normalize_v3({'success':True,'obj':[{'client':r,'traffic':r['traffic']}]})[0]['sub'],SUB)
 def test_v2_string_or_object_settings(self):
  settings={'clients':[{'email':'a','subId':SUB,'id':'uuid'}]}
  for value in [settings,json.dumps(settings)]:
   r={'success':True,'obj':[{'id':3,'settings':value,'clientStats':[{'email':'a','up':10,'down':20,'id':5}]}]}
   self.assertEqual(m.normalize_v2(r)[0]['used'],30)
 def test_v2_duplicate_global_traffic_id_not_double_counted(self):
  row={'id':7,'subId':SUB,'email':'a','up':1,'down':2}
  self.assertEqual(len(m.normalize_v2({'success':True,'obj':[{'id':1,'clientStats':[row]},{'id':2,'clientStats':[row]}]})),1)
 def test_invalid_schema_not_silently_zeroed(self):
  for payload in [{'success':False,'obj':[]},{'success':True,'obj':{}},{'success':True,'obj':[{'subId':SUB,'id':1,'traffic':{'up':5}}]}]:
   with self.assertRaises(m.Unsupported):m.normalize_v3(payload)
 def test_auth_failure_does_not_probe_fallback(self):
  api=object.__new__(m.API);api.c={'api_token':'test','api_mode':'auto'};calls=[]
  def request(path):calls.append(path);raise m.Authentication('no')
  api.request=request
  with self.assertRaises(m.Authentication):api.collect()
  self.assertEqual(len(calls),1)
 def test_auto_fallback_for_missing_v3_route(self):
  api=object.__new__(m.API);api.c={'api_token':'test','api_mode':'auto'}
  def request(path):
   if 'clients/list' in path:raise m.Unsupported('missing')
   return {'success':True,'obj':[]}
  api.request=request;self.assertEqual(api.collect(),([], 'v2'))
 def test_selected_adapter_does_not_switch_after_temporary_shape_error(self):
  api=object.__new__(m.API);api.c={'api_token':'test','api_mode':'auto'};api.selected='v3';calls=[]
  def request(path):calls.append(path);raise m.Unsupported('temporary malformed data')
  api.request=request
  with self.assertRaises(m.Unsupported):api.collect()
  self.assertEqual(calls,['panel/api/clients/list'])
 def test_network_error_does_not_trigger_api_fallback(self):
  api=object.__new__(m.API);api.c={'api_token':'test','api_mode':'auto'};calls=[]
  def request(path):calls.append(path);raise m.Unavailable('offline')
  api.request=request
  with self.assertRaises(m.Unavailable):api.collect()
  self.assertEqual(len(calls),1)
 def test_first_observation_is_baseline_not_invented_past(self):
  m.ingest(self.db,[record(999)],1000,60);h=m.history(self.db,SUB,1001,60)
  self.assertEqual(h['points'][0]['used'],0)
 def test_counter_delta(self):
  m.ingest(self.db,[record(100)],1000,60);m.ingest(self.db,[record(150)],1060,60)
  self.assertEqual(m.history(self.db,SUB,1061,60)['points'][-1]['used'],50)
 def test_reset_is_nonnegative_and_marked_gap(self):
  m.ingest(self.db,[record(100)],1000,60);m.ingest(self.db,[record(5,1)],1060,60)
  p=m.history(self.db,SUB,1061,60)['points'][-1];self.assertEqual(p['used'],5);self.assertTrue(p['gap'])
 def test_identity_reuse_does_not_count_old_account(self):
  m.ingest(self.db,[record(100)],1000,60);m.ingest(self.db,[record(500,generation='new')],1060,60)
  self.assertEqual(m.history(self.db,SUB,1061,60)['points'][-1]['used'],0)
 def test_collection_gap_not_attributed(self):
  m.ingest(self.db,[record(100)],1000,60);m.ingest(self.db,[record(500)],2000,60)
  self.assertEqual(m.history(self.db,SUB,2001,60)['points'][-1]['used'],0)
 def test_removed_sub_revoked_after_successful_snapshot(self):
  m.ingest(self.db,[record(1)],1000,60);m.ingest(self.db,[],1060,60)
  self.assertIsNone(m.history(self.db,SUB,1061,60))
 def test_subscription_isolation_and_stale(self):
  m.ingest(self.db,[record(1)],1000,60)
  self.assertIsNone(m.history(self.db,OTHER,1001,60));self.assertIsNone(m.history(self.db,SUB,5000,60));self.assertIsNone(m.history(self.db,'../bad',1001,60))
 def test_secrets_not_stored_in_history_response(self):
  m.ingest(self.db,[record(123,generation='private-uuid')],1000,60)
  h=json.dumps(m.history(self.db,SUB,1001,60));self.assertNotIn(SUB,h);self.assertNotIn('private-uuid',h)
 def test_config_rejects_external_plain_http(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'c.json';p.write_text(json.dumps({'panel_url':'http://example.com/secretbase','api_token':'test'}))
   with self.assertRaises(ValueError):m.load_config(p)
 def test_redirects_never_forward_credentials(self):self.assertIsNone(m.NoRedirect().redirect_request(None,None,None,None,None,None))
if __name__=='__main__':unittest.main()
