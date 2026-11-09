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

class UsageAttachTests(unittest.TestCase):
 def test_usage_attachment_preserves_profile_status_and_future_updates(self):
  from status_attach import prepare_usage
  raw=(ROOT/'sub.html').read_text();text,_=render(raw,'Private Brand','blue','ghost')
  text=prepare(text,18090);text=prepare_usage(text,18090)
  self.assertIn('name="ghost-usage-port" content="18090"',text)
  self.assertEqual(re.findall(r'\{\{.*?\}\}|\{%.*?%\}',raw,re.S),re.findall(r'\{\{.*?\}\}|\{%.*?%\}',text,re.S))
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'index.html';p.write_text(text)
   _,saved=render(raw,'','','keep',previous=p)
   self.assertEqual(saved['brand'],'Private Brand');self.assertEqual(saved['status_port'],18090);self.assertEqual(saved['usage_port'],18090)
