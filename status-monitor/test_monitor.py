import importlib.util,json,socket,sqlite3,tempfile,threading,time,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('monitor',Path(__file__).with_name('monitor.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class MonitorTests(unittest.TestCase):
 def test_no_fake_uptime(self):
  r=m.summarize([],100000,60)
  self.assertIsNone(r['availability_pct']);self.assertEqual(r['state'],'unknown');self.assertEqual(r['history'],[None]*24)
 def test_discrete_sample_ratio_partial_coverage(self):
  r=m.summarize([(99500,1,5),(99600,0,None),(99700,1,8)],100000,120)
  self.assertEqual(r['availability_pct'],66.67);self.assertEqual(r['observed_seconds'],200);self.assertEqual(r['samples'],3)
 def test_stale_samples_are_unknown(self):
  self.assertEqual(m.summarize([(1,1,5)],1000,60)['state'],'unknown')
 def test_failed_three_samples_are_down(self):
  self.assertEqual(m.summarize([(98,0,None),(99,0,None),(100,0,None)],100,60)['state'],'down')
 def test_mixed_is_unstable(self):
  self.assertEqual(m.summarize([(99,1,2),(100,0,None)],100,60)['state'],'unstable')
 def test_unknown_history_gaps_not_green(self):
  r=m.summarize([(99999,1,1)],100000,60)
  self.assertEqual(r['history'].count(None),23);self.assertEqual(r['history'][-1],100)
 def test_identity_normalizes_case_and_dot(self):
  self.assertEqual(m.endpoint_id('Node.Example.',443),m.endpoint_id('node.example',443))
 def test_config_rejects_duplicates(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'c.json';f.write_text(json.dumps({'targets':[{'host':'node.example','port':443},{'host':'NODE.EXAMPLE.','port':443}]}))
   with self.assertRaises(ValueError):m.config(f)
 def test_tcp_check_uses_real_local_listener(self):
  with socket.socket() as server:
   server.bind(('127.0.0.1',0));server.listen();port=server.getsockname()[1]
   self.assertTrue(m.check({'host':'127.0.0.1','port':port},.1)[0])
  self.assertFalse(m.check({'host':'127.0.0.1','port':port},.1)[0])
 def test_export_omits_host_and_credentials(self):
  db=m.open_db(':memory:');target={'host':'hidden.example','port':443,'id':m.endpoint_id('hidden.example',443),'country':'DE'}
  out=m.snapshot(db,{'targets':[target],'interval_seconds':60,'probe_label':'Outside'})
  self.assertNotIn('hidden.example',json.dumps(out));self.assertEqual(out['measurement'],'tcp_connect_samples');db.close()
 def test_state_survives_reopen(self):
  with tempfile.TemporaryDirectory() as d:
   file=str(Path(d)/'state.db');db=m.open_db(file);db.execute('INSERT INTO samples VALUES (?,?,?,?)',('n',100,1,5));db.commit();db.close();db=m.open_db(file)
   self.assertEqual(db.execute('SELECT COUNT(*) FROM samples').fetchone()[0],1);db.close()
if __name__=='__main__':unittest.main()
