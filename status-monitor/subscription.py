"""Admin-configured subscription import. No client-provided scan targets or URL logs."""
import base64,html,json,re,urllib.parse,urllib.request
LIMIT=2*1024*1024

def validate_url(url):
 p=urllib.parse.urlsplit(url)
 if p.scheme not in ('http','https') or not p.hostname or p.username or p.password or p.fragment or len(url)>4096:
  raise ValueError('Subscription must be an HTTP(S) URL without URL credentials or fragment')
 return p

def b64(text):
 text=text.strip();return base64.b64decode(text+'='*((-len(text))%4),altchars=b'-_',validate=True).decode('utf-8')

def targets(text):
 if len(text.encode())>LIMIT:raise ValueError('Subscription is too large')
 if '<html' in text.lower() or '<!doctype' in text.lower():
  match=re.search(r'\blinks\s*:\s*`(.*?)`',text,re.S)
  if not match:raise ValueError('Subscription response contains no supported links')
  text=html.unescape(match[1]).replace('\\n','\n').replace('\\/','/')
 if not re.search(r'(?im)^\s*(?:vless|trojan|vmess|ss)://',text):
  try:text=b64(re.sub(r'\s','',text))
  except (ValueError,UnicodeError):raise ValueError('Unsupported subscription format') from None
 result=[];seen=set()
 for line in text.splitlines():
  line=line.strip()
  try:
   if line.startswith('vmess://'):
    d=json.loads(b64(line[8:]));host=d['add'];port=int(d['port'])
    if d.get('net') in ('quic','kcp'):continue
   elif line.startswith(('vless://','trojan://','ss://')):
    if line.startswith('ss://') and '@' not in line:
     line='ss://'+b64(line[5:].split('#')[0])
    u=urllib.parse.urlsplit(line);host=u.hostname;port=u.port
    if urllib.parse.parse_qs(u.query).get('type',[''])[0] in ('quic','kcp'):continue
   else:continue
   if not host or not port or not 1<=port<=65535 or not re.fullmatch(r'[a-zA-Z0-9._:\-]{1,253}',host):continue
   host=host.lower().rstrip('.');key=(host,port)
   if key in seen:continue
   seen.add(key);result.append({'host':host,'port':port,'country':''})
  except (ValueError,KeyError,TypeError,UnicodeError):continue
 if not result:raise ValueError('No supported TCP endpoints found; use a raw/base64 subscription link')
 if len(result)>64:raise ValueError('Subscription exceeds 64 unique TCP endpoints')
 return result

class SameOrigin(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  old=validate_url(req.full_url);new=validate_url(newurl)
  if (old.scheme,old.hostname,old.port)!=(new.scheme,new.hostname,new.port):raise ValueError('Cross-origin subscription redirect refused')
  return super().redirect_request(req,fp,code,msg,headers,newurl)

def fetch(url):
 validate_url(url)
 req=urllib.request.Request(url,headers={'User-Agent':'v2rayNG','Accept':'text/plain','Accept-Encoding':'identity'})
 with urllib.request.build_opener(SameOrigin()).open(req,timeout=10) as response:
  data=response.read(LIMIT+1)
 if len(data)>LIMIT:raise ValueError('Subscription is too large')
 return targets(data.decode('utf-8-sig'))
