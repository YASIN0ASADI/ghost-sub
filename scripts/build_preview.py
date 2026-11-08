#!/usr/bin/env python3
"""Generate safe static illustrative fixtures, never real panel credentials."""
from pathlib import Path
import re, json, time, hashlib
from branding import render
ROOT = Path(__file__).resolve().parent.parent
out = ROOT / 'preview';out.mkdir(exist_ok=True)
now = int(time.time()*1000)
points=[{'t':now-(60-i)*86400000,'used':int(3.2*1024**3*i/60)} for i in range(61)]
links = '\n'.join('vless://00000000-0000-4000-8000-000000000001@'+name.lower()+'.example.invalid:443?security=tls&type=tcp#'+name for name in ['Poland','Germany','Netherlands','Finland'])
demo_feed={'schema':1,'generated_at':now//1000,'interval_seconds':60,'probe_label':'DEMO · outside probe','measurement':'tcp_connect_samples','nodes':{}}
for name,code,state in [('Poland','PL','up'),('Germany','DE','unstable'),('Netherlands','NL','down')]:
 key=hashlib.sha256((name.lower()+'.example.invalid:443').encode()).hexdigest()[:24]
 good={'up':1190,'unstable':1080,'down':900}[state]
 demo_feed['nodes'][key]={'state':state,'country':code,'last_checked':now//1000-20,'samples':1200,'successful_samples':good,'availability_pct':100*good/1200,'observed_seconds':71400,'tcp_connect_ms':95,'history':[None]*4+({'up':[100,100,100,99,100,100,98,100,100,100,99,100,100,100,100,98,100,100,100,100],'unstable':[100,100,96,100,87,100,90,95,70,92,100,98,85,100,88,90,95,80,100,90],'down':[100,100,100,100,100,100,100,100,100,100,100,100,100,100,90,75,50,30,0,0]}[state])}
for panel in ['sub','marzban','pasarguard']:
 for theme in ['red','green','blue']:
  source,_ = render((ROOT/(panel+'.html')).read_text(),'YOUR BRAND',theme,'ghost')
  source=re.sub(r'\{% for link in .*?%\}.*?\{% endfor %\}',lambda _:links,source,flags=re.S)
  source=re.sub(r'\{\{ range \.links \}\}.*?\{\{ end \}\}',lambda _:links,source,flags=re.S)
  def value(m):
   expr=m[0]
   if 'username' in expr or 'emails' in expr:return 'demo_user'
   if 'data_limit' in expr or 'totalByte' in expr:return str(15*1024**3)
   if 'used_traffic' in expr or 'uploadByte' in expr:return str(int(3.2*1024**3))
   if 'status.value' in expr:return 'active'
   if 'enable' in expr:return 'true'
   if 'subUrl' in expr:return 'https://subscription.example.invalid/sub/demo1234567890123'
   if 'online_at' in expr:return str(now-180000)
   if 'expire' in expr:return '0'
   if 'links' in expr:return links
   return '0'
  source=re.sub(r'\{\{.*?\}\}',value,source,flags=re.S)
  source=source.replace('subUrl: window.location.href.split(\'?\')[0]',"subUrl: 'https://subscription.example.invalid/sub/demo1234567890123'")
  # QA fixture only: never send demonstration links to QR/image/doctor providers.
  source=source.replace('<body>', '<body><div style="position:fixed;bottom:8px;left:8px;z-index:9999;background:#19191c;color:#ddd;padding:4px 9px;border-radius:8px;font:11px sans-serif;pointer-events:none">DESIGN PREVIEW · SAMPLE DATA</div>',1)
  source=source.replace('let points = null;', 'let points = '+json.dumps(points)+';')
  source=source.replace('let ghostFeed=null;', 'let ghostFeed='+json.dumps(demo_feed)+'; ghostFeed.generated_at=Math.floor(Date.now()/1000); Object.values(ghostFeed.nodes).forEach(n=>n.last_checked=ghostFeed.generated_at-20);')
  if panel=='sub':
   source=source.replace('<meta name="ghost-usage-base" content="">','<meta name="ghost-usage-base" content="/ghost-usage/">')
   data={'schema':1,'source':'sampled_3xui_counters','updated_at':now//1000,'points':points}
   source=source.replace('let ghostUsageCache=null;', 'let ghostUsageCache={at:Infinity,data:'+json.dumps(data)+'};ghostUsageCache.data.updated_at=Math.floor(Date.now()/1000);')
  name = 'index.html' if (panel,theme)==('marzban','red') else panel+'-'+theme+'.html'
  (out/name).write_text(source)
points=[{'t':now-(60-i)*86400000,'used':int(3.2*1024**3*i/60)} for i in range(61)]
(out/'usage_demo_user.json').write_text(json.dumps({'username':'demo_user','points':points}))
(out/'manifest.json').write_text(json.dumps({'name':'Ghost Preview','display':'standalone','start_url':'./'}))
print('Built 9 illustrative panel/theme fixtures in preview/')
