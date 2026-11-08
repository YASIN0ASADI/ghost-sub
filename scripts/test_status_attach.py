import pathlib,re,tempfile,unittest
from branding import render,settings
from status_attach import prepare
ROOT=pathlib.Path(__file__).resolve().parent.parent
class AttachTests(unittest.TestCase):
 def test_existing_templates_keep_brand_and_bindings(self):
  for panel in ['sub','marzban','pasarguard']:
   source=(ROOT/(panel+'.html')).read_text()
   original,_=render(source,'My Brand','blue','ghost')
   # Also exercise previously installed versions without the new meta tag.
   original=original.replace('<meta name="ghost-status-port" content="">','')
   output=prepare(original,18090)
   self.assertEqual(re.findall(r'\{\{.*?\}\}|\{%.*?%\}',original,re.S),re.findall(r'\{\{.*?\}\}|\{%.*?%\}',output,re.S))
   self.assertIn('name="ghost-status-port" content="18090"',output)
   self.assertIn('My Brand',output)
   with tempfile.TemporaryDirectory() as d:
    old=pathlib.Path(d)/'index.html';old.write_text(output)
    self.assertEqual(settings(old)['status_port'],18090)
    updated,state=render(source,'','','keep',previous=old)
    self.assertEqual(state['status_port'],18090)
    self.assertIn('name="ghost-status-port" content="18090"',updated)
 def test_bad_inputs(self):
  for port in [0,100,65536]:
   with self.assertRaises(ValueError):prepare('<html></html>',port)
  with self.assertRaises(ValueError):prepare('<html>old template</html>',18090)
if __name__=='__main__':unittest.main()
