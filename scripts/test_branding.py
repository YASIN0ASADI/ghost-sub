import base64, binascii, json, re, struct, subprocess, tempfile, unittest, zlib
from pathlib import Path
from branding import render, settings, image_uri, valid_https, LIMIT
ROOT=Path(__file__).resolve().parent.parent


def png(w=1,h=1):
 def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',binascii.crc32(k+d)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0\xff\0\0\xff'))+chunk(b'IEND',b'')


class BrandingTests(unittest.TestCase):
 def test_all_panel_theme_and_logo_combinations_preserve_bindings(self):
  for panel in ['sub','marzban','pasarguard']:
   raw=(ROOT/(panel+'.html')).read_text()
   bindings=re.findall(r'\{\{.*?\}\}|\{%.*?%\}',raw,re.S)
   for theme in ['red','green','blue']:
    for mode in ['ghost','none']:
     out,saved=render(raw,'AFRA',theme,mode)
     self.assertEqual(bindings,re.findall(r'\{\{.*?\}\}|\{%.*?%\}',out,re.S))
     self.assertEqual('id="logo-icon"' in out,mode=='ghost')
     self.assertEqual(saved['theme'],theme)
     self.assertIn("getElementById('logo-icon')?.",out)
 def test_custom_logo_and_update_without_original_file(self):
  with tempfile.TemporaryDirectory() as temp:
   logo=Path(temp)/'my logo.png';logo.write_bytes(png())
   source=(ROOT/'marzban.html').read_text()
   output,state=render(source,'برند من','green','custom',str(logo))
   previous=Path(temp)/'previous.html';previous.write_text(output)
   logo.unlink()
   updated,newstate=render(source,'','','keep',previous=str(previous))
   self.assertEqual(state,newstate)
   self.assertIn('data:image/png;base64,',updated)
   self.assertNotIn('id="logo-icon"',updated)
 def test_remove_previous_custom_logo(self):
  out,state=render((ROOT/'sub.html').read_text(),'Brand','red','none')
  self.assertNotIn('class="logo-wrap"',out)
 def test_brand_does_not_create_template_or_html_or_script(self):
  brand='A & <test> " \' ${alert(1)} {{7*7}} {%x%} ` \\'
  out,state=render((ROOT/'sub.html').read_text(),brand,'blue','ghost')
  self.assertNotIn(brand,out)
  self.assertIn('&amp;',out)
  self.assertEqual(state['brand'],brand)
 def test_bad_images_rejected(self):
  for bad in [b'<svg></svg>',png()[:-1],b'\0'*(LIMIT+1),png(9000,1),b'not an image']:
   with self.assertRaises(ValueError):image_uri(bad)
 def test_both_raster_mime_types(self):
  self.assertTrue(image_uri(png()).startswith('data:image/png;base64,'))
  # Real WebP fixture from a 1x1 lossy image.
  webp=base64.b64decode('UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA')
  self.assertTrue(image_uri(webp).startswith('data:image/webp;base64,'))
 def test_https_only(self):
  valid_https('https://example.invalid/logo.png')
  for bad in ['http://example.invalid/a','file:///tmp/a','https://user:pass@example.invalid/a']:
   with self.assertRaises(ValueError):valid_https(bad)
 def test_old_template_fails_before_output(self):
  with self.assertRaises(ValueError):render('<html>old</html>','B','red','ghost')
 def test_missing_brand_fails(self):
  with self.assertRaises(ValueError):render((ROOT/'sub.html').read_text(),'','red','ghost')
 def test_status_feed_persist_disable_and_validate(self):
  with tempfile.TemporaryDirectory() as d:
   source=(ROOT/'sub.html').read_text()
   out,state=render(source,'B','red','ghost',status_feed='/ghost-status.json')
   previous=Path(d)/'old.html';previous.write_text(out)
   _,preserved=render(source,'','','keep',previous=previous)
   self.assertEqual(preserved['status_feed'],'/ghost-status.json')
   out,state=render(source,'','','keep',previous=previous,status_feed='')
   self.assertEqual(state['status_feed'],'')
   for bad in ['http://example.invalid/status','//example.invalid/status','javascript:alert(1)']:
    with self.assertRaises(ValueError):render(source,'B','red','ghost',status_feed=bad)
 def test_usage_route_is_same_origin_only_and_persisted(self):
  source=(ROOT/'sub.html').read_text()
  with tempfile.TemporaryDirectory() as d:
   out,state=render(source,'B','red','ghost',usage_base='/ghost-usage/')
   previous=Path(d)/'old.html';previous.write_text(out)
   _,saved=render(source,'','','keep',previous=previous)
   self.assertEqual(saved['usage_base'],'/ghost-usage/')
  for bad in ['https://evil.example/','//evil.example/','/bad?secret=x','/bad\\path']:
   with self.assertRaises(ValueError):render(source,'B','red','ghost',usage_base=bad)
 def test_tracker_sources_unchanged(self):
  original=ROOT.parent/'upload'
  if not (original/'tracker.py').is_file():self.skipTest('Baseline upload not available in this checkout')
  self.assertEqual((original/'tracker.py').read_bytes(),(ROOT/'tracker/tracker.py').read_bytes())
  self.assertEqual((original/'ghost-tracker.service').read_bytes(),(ROOT/'tracker/ghost-tracker.service').read_bytes())


if __name__=='__main__':unittest.main()
