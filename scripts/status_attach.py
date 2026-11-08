"""Attach the monitor to an installed original template; retain all branding/data bindings."""
import base64,json,os,re,stat,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def prepare(text,port):
 if not isinstance(port,int) or not 1024<=port<=65535:raise ValueError('Invalid monitor port')
 marker=re.compile(r'<!-- GHOST_SETTINGS:([A-Za-z0-9+/=]+) -->')
 found=marker.search(text)
 if not found:raise ValueError('Install the current Ghost Sub template first')
 settings=json.loads(base64.b64decode(found[1],validate=True));settings['status_port']=port
 encoded=base64.b64encode(json.dumps(settings,ensure_ascii=False).encode()).decode()
 text=marker.sub(lambda m:'<!-- GHOST_SETTINGS:'+encoded+' -->',text)
 a=text.index('/* Ghost Sub status:');b=text.index('\nlet soundEnabled',a)
 text=text[:a]+(ROOT/'scripts/status_ui.js').read_text().rstrip()+'\n'+text[b:]
 port_meta='<meta name="ghost-status-port" content="'+str(port)+'">'
 if re.search(r'<meta name="ghost-status-port" content="[^"]*">',text):
  text=re.sub(r'<meta name="ghost-status-port" content="[^"]*">',lambda m:port_meta,text,count=1)
 else:text=text.replace('</head>',port_meta+'\n</head>',1)
 return text

def write(path,text):
 path=Path(path)
 if path.is_symlink():raise ValueError('Template symlink refused')
 info=path.stat();fd,tmp=tempfile.mkstemp(prefix='.ghost-monitor-',dir=path.parent)
 try:
  with os.fdopen(fd,'w') as f:f.write(text)
  os.chmod(tmp,stat.S_IMODE(info.st_mode));os.chown(tmp,info.st_uid,info.st_gid);os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
