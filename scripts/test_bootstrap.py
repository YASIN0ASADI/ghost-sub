"""Exercise process-substitution bootstrap with a local archive and blocked host writes."""
import io,os,pathlib,shlex,subprocess,sys,tarfile,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
class Bootstrap(unittest.TestCase):
 def check_archive(self,missing=False):
  with tempfile.TemporaryDirectory() as d:
   base=pathlib.Path(d);bin=base/'bin';bin.mkdir();archive=base/'source.tgz'
   with tarfile.open(archive,'w:gz') as tar:
    for p in ROOT.rglob('*'):
     if p.is_file() and '.git' not in p.parts and 'preview' not in p.parts and '__pycache__' not in p.parts:
      if missing and p.name=='install_template.sh':continue
      tar.add(p,arcname='ghost-sub-main/'+str(p.relative_to(ROOT)))
   curl=bin/'curl';curl.write_text('#!/bin/bash\nwhile [[ $# -gt 0 ]]; do if [[ "$1" == -o ]]; then cp "$MOCK_ARCHIVE" "$2"; exit; fi; shift; done\nexit 2\n');curl.chmod(0o755)
   py=bin/'python3';py.write_text('#!'+sys.executable+'\n'+'''import os,sys,pathlib,subprocess
args=sys.argv[1:]
if args[1]=='-':os.execv(REAL,[REAL,*args])
if args[1].endswith('/scripts/install_manager.py'):
 root=pathlib.Path(args[1]).parent.parent
 assert (root/'scripts/install_template.sh').is_file()
 assert (root/'traffic-history/history.py').is_file()
 pathlib.Path(os.environ['PROOF']).write_text('prepared')
 sys.exit(0)
if args[1]=='/opt/ghost-sub-manager/scripts/manage.py':
 os.execv(REAL,[REAL,'-I',MANAGER])
raise SystemExit('Unexpected Python command')
'''.replace('REAL',repr(sys.executable)).replace('MANAGER',repr(str(ROOT/'scripts/manage.py'))));py.chmod(0o755)
   env={**os.environ,'PATH':str(bin)+':'+os.environ['PATH'],'MOCK_ARCHIVE':str(archive),'PROOF':str(base/'proof')}
   # The runner is root in development; no host installer is executed by the mock.
   r=subprocess.run(['bash','-c','bash <(cat '+shlex.quote(str(ROOT/'install.sh'))+')'],input='0\n',text=True,capture_output=True,env=env)
   return r,(base/'proof').exists()
 @unittest.skipUnless(os.geteuid()==0,'bootstrap requires root')
 def test_complete_one_liner_opens_menu(self):
  r,proof=self.check_archive();self.assertEqual(r.returncode,0,r.stderr);self.assertTrue(proof);self.assertIn('Ghost Sub Manager',r.stdout)
 @unittest.skipUnless(os.geteuid()==0,'bootstrap requires root')
 def test_incomplete_bundle_stops_before_install(self):
  r,proof=self.check_archive(True);self.assertNotEqual(r.returncode,0);self.assertFalse(proof)
if __name__=='__main__':unittest.main()
