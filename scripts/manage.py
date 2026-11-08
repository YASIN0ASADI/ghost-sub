#!/usr/bin/env python3
"""Ghost Sub terminal manager. No automatic operations on entry."""
import importlib.util,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PANELS={'1':('3X-UI',Path('/etc/3x-ui/sub_templates/my-theme')),'2':('Pasarguard',Path('/var/lib/pasarguard/templates/subscription')),'3':('Marzban',Path('/var/lib/marzban/templates/subscription'))}

def run(args):
    try:return subprocess.run([str(a) for a in args],check=False).returncode
    except OSError:print('Command unavailable.');return 1

def root_terminal():
    if os.geteuid()!=0 or not sys.stdin.isatty():print('Changes require root and an interactive terminal.');return False
    return True

def confirm(text):return input(text+' [y/N]: ').strip().lower() in ('y','yes')

def panel():
    for k,(name,_) in PANELS.items():print(k+') '+name)
    key=input('Panel: ').strip()
    if key not in PANELS:raise ValueError('Invalid panel')
    return key,PANELS[key]

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def diagnostics():
    print('\nRead-only checks; no network probes or service restart.')
    branding=module(ROOT/'scripts/branding.py','branding')
    for _,(name,folder) in PANELS.items():
        file=folder/'index.html'
        if not file.exists():print(name+': template not installed');continue
        try:
            state=branding.settings(file)
            print(name+': template present; saved branding '+('present' if state else 'legacy/missing'))
            print('  Server feed configured: '+str(bool(state.get('status_feed'))))
            print('  3X-UI history route configured: '+str(bool(state.get('usage_base'))))
        except (OSError,ValueError):print(name+': unreadable/invalid template settings')
    for unit in ['ghost-tracker.service','ghost-history.service','ghost-status.service','ghost-gateway.service']:
        print('\n'+unit)
        run(['systemctl','show',unit,'--no-pager','-p','LoadState','-p','ActiveState','-p','SubState','-p','NRestarts'])
    file=Path('/etc/ghost-history/config.json');db=Path('/var/lib/ghost-history/history.sqlite3')
    if file.exists():
        try:module(ROOT/'traffic-history/history.py','history').load_config(file);print('Private 3X-UI history config: valid (credentials omitted)')
        except (OSError,ValueError):print('Private 3X-UI history config: invalid/unreadable')
    if db.exists():
        import sqlite3,time
        try:
            conn=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True)
            row=conn.execute('SELECT MAX(updated) FROM totals').fetchone();conn.close()
            print('Latest successful history sample age: '+(str(max(0,int(time.time()-row[0])))+' seconds' if row and row[0] else 'none'))
        except sqlite3.Error:print('History database unavailable')
    print('\nHTTP reverse-proxy/browser route and real panel compatibility must be checked separately; file existence is not end-to-end health.')

def history_setup():
    config=Path('/etc/ghost-history/config.json')
    print('Separate optional 3X-UI collector; token/password stays in a private server file.')
    if not confirm('Configure/install the collector (no automatic start)?'):return
    if run(['python3','-I',ROOT/'traffic-history/history.py','--config',config,'--configure']):return
    # The service needs group-read; installer preserves the existing private file.
    if run(['bash',ROOT/'traffic-history/install.sh',config]):return
    import grp
    os.chown(config,0,grp.getgrnam('ghost-history').gr_gid);os.chmod(config,0o640)
    print('Next: configure the same-origin /ghost-usage/ proxy route and select it in template appearance setup.')
    if confirm('Start/restart only ghost-history.service now?'):run(['systemctl','restart','ghost-history.service'])
    if confirm('Enable ghost-history.service at boot?'):run(['systemctl','enable','ghost-history.service'])

def status_setup():
    import getpass
    config=Path('/etc/ghost-status/config.json')
    importer=module(ROOT/'status-monitor/subscription.py','subscription')
    print('1) Automatic: import all TCP endpoints from ONE subscription link (default)')
    print('2) Enter TCP endpoints manually')
    if config.exists():print('3) Keep existing monitor settings')
    mode=input('Mode [1]: ').strip() or '1'
    candidate=None
    if mode=='3' and config.exists():pass
    elif mode in ('1','2'):
        probe=input('Probe label [This server]: ').strip() or 'This server'
        if mode=='1':
            print('Paste your own full subscription URL locally. It stays in the private server config.')
            print('For HTTP subscriptions the link travels without encryption; HTTPS is preferred.')
            url=getpass.getpass('Subscription URL (hidden): ').strip()
            try:items=importer.fetch(url)
            except Exception:
                print('Could not read supported TCP links. No settings changed; use the raw/base64 subscription URL.');return
            candidate={'probe_label':probe,'interval_seconds':60,'timeout_seconds':3,'listen_port':19191,'targets':items,'subscription_source':url}
            print(str(len(items))+' unique TCP endpoints found. The list refreshes automatically every 15 minutes.')
        else:
            items=[]
            while len(items)<64:
                host=input('Node host (Enter to finish): ').strip()
                if not host:break
                items.append({'host':host,'port':int(input('Node TCP port: ')),'country':input('Country ISO2 (optional): ').strip().upper()})
            candidate={'probe_label':probe,'interval_seconds':60,'timeout_seconds':3,'listen_port':19191,'targets':items}
        m=module(ROOT/'status-monitor/monitor.py','monitor')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'config.json';p.write_text(json.dumps(candidate));m.config(p)
            if not confirm('Save targets and install/update monitor (no automatic start)?'):return
            if run(['bash',ROOT/'status-monitor/install.sh',p]):return
            # Installer intentionally retains existing config; replace only after explicit save above.
            import grp
            fd,tmp=tempfile.mkstemp(prefix='.config-',dir=config.parent)
            try:
                with os.fdopen(fd,'w') as f:json.dump(candidate,f)
                os.chown(tmp,0,grp.getgrnam('ghost-status').gr_gid);os.chmod(tmp,0o640);os.replace(tmp,config)
            finally:
                if os.path.exists(tmp):os.unlink(tmp)
    else:raise ValueError('Invalid mode')
    if candidate is None and run(['bash',ROOT/'status-monitor/install.sh',config]):return
    print('Monitor targets configured. A domain-free subscription entrance can connect the chart automatically.')
    if confirm('Start/restart only ghost-status.service now?'):run(['systemctl','restart','ghost-status.service','ghost-gateway.service'])
    if confirm('Enable ghost-status.service at boot?'):run(['systemctl','enable','ghost-status.service','ghost-gateway.service'])
    if confirm('Connect the chart using an IP:port entrance now?'):gateway_setup()

def gateway_setup():
    import getpass,socket,urllib.parse
    source=''
    monitor=Path('/etc/ghost-status/config.json')
    if monitor.is_file():source=json.loads(monitor.read_text()).get('subscription_source','')
    if not source:source=getpass.getpass('Existing full subscription URL (hidden): ').strip()
    importer=module(ROOT/'status-monitor/subscription.py','subscription')
    url=importer.validate_url(source)
    port=int(input('New public subscription port [18090]: ').strip() or '18090')
    upstream=int(input('LOCAL HTTP subscription port ['+str(url.port or 2096)+']: ').strip() or str(url.port or 2096))
    host=input('Public server IP ['+url.hostname+']: ').strip() or url.hostname
    import re
    if not re.fullmatch(r'[A-Za-z0-9.\-]+',host):raise ValueError('Invalid public IPv4/DNS host')
    prefix=url.path.rsplit('/',1)[0]+'/'
    candidate={'listen_port':port,'upstream_port':upstream,'path_prefix':prefix}
    gateway=module(ROOT/'gateway/server.py','gateway')
    destination=Path('/etc/ghost-gateway/config.json')
    existing={}
    if destination.is_file():existing=json.loads(destination.read_text())
    active=subprocess.run(['systemctl','is-active','--quiet','ghost-gateway.service'],capture_output=True).returncode==0
    with tempfile.TemporaryDirectory() as d:
        file=Path(d)/'config.json';file.write_text(json.dumps(candidate));gateway.config(file)
        if not (active and existing.get('listen_port')==port):
            try:
                with socket.socket() as listener:listener.bind(('0.0.0.0',port))
            except OSError:print('Public port already in use; choose another port. Nothing changed.');return
        print('This adds an HTTP subscription entrance on port '+str(port)+'. No domain or Apache/Nginx changes.')
        print('Existing subscription port and mini-app stay in place. Subscription links are private; HTTP is unencrypted.')
        if not confirm('Install, start/restart and enable this gateway at boot?'):return
        if run(['bash',ROOT/'gateway/install.sh',file]):return
    if run(['systemctl','restart','ghost-gateway.service']):return
    if run(['systemctl','enable','ghost-gateway.service']):return
    public=urllib.parse.urlunsplit(('http',host+':'+str(port),url.path,url.query,''))
    print('Use this NEW subscription link in the browser/apps (do not post it publicly):')
    print(public)
    print('Status feed is injected automatically on this entrance; no Status feed field needed.')
    print('If external access is blocked, allow only TCP '+str(port)+' in your existing firewall/provider rules.')
    print('The old subscription URL still works but does not use this gateway.')

def rollback():
    key,(name,folder)=panel();choices=[]
    for p in sorted(Path('/root').glob('ghost-sub-backup.*'),reverse=True):
        if p.is_symlink() or not p.is_dir():continue
        try:
            meta=json.loads((p/'panel.json').read_text())
            if meta.get('panel')==key and meta.get('destination')==str(folder/'index.html') and (p/'index.html').is_file():choices.append(p)
        except (OSError,ValueError):continue
    if not choices:print('No matching tagged backup. Legacy untagged backups require manual review.');return
    for i,p in enumerate(choices,1):print(str(i)+') '+p.name)
    index=int(input('Backup number: '))-1
    if not 0<=index<len(choices):raise ValueError('Invalid backup')
    chosen=choices[index]
    if not confirm('Restore only '+name+' template/manifest from '+chosen.name+'?'):return
    rescue=Path(tempfile.mkdtemp(prefix='ghost-sub-before-restore.',dir='/root'));os.chmod(rescue,0o700)
    for filename in ['index.html','manifest.json']:
        target=folder/filename;source=chosen/filename
        if target.is_symlink() or source.is_symlink():raise ValueError('Symlink destination/source refused')
        if source.is_file():
            if target.is_file():shutil.copy2(target,rescue/filename)
            fd,tmp=tempfile.mkstemp(prefix='.ghost-restore-',dir=folder)
            with os.fdopen(fd,'wb') as f:f.write(source.read_bytes())
            os.chmod(tmp,0o644);os.replace(tmp,target)
    print('Restored. No service restarted; recovery copy: '+str(rescue))
    print('Reload the selected panel at an appropriate time; active connections may be affected.')

def main():
    while True:
        print('\nGhost Sub Manager\n1) Install/apply bundled template version\n2) Change brand/logo/default theme (installer)\n3) Configure 3X-UI usage history\n4) Configure server reachability monitor\n5) Read-only installation checks\n6) Restore matching template backup\n7) Connect chart without a domain (IP:port)\n0) Exit')
        try:
            choice=input('Select: ').strip()
            if choice=='0':return
            if choice=='5':diagnostics();continue
            if choice not in ('1','2','3','4','6','7'):print('Invalid selection');continue
            if not root_terminal():continue
            if choice in ('1','2'):run(['bash',ROOT/'scripts/install_template.sh'])
            elif choice=='3':history_setup()
            elif choice=='4':status_setup()
            elif choice=='6':rollback()
            elif choice=='7':gateway_setup()
        except (EOFError,KeyboardInterrupt):print('\nClosed.');return
        except (OSError,ValueError):print('Operation could not complete; no credentials are printed. Review configuration privately.')
if __name__=='__main__':main()
