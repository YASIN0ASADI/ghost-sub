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
    print('After collection starts, option 8 connects history to the original subscription page.')
    if confirm('Start/restart only ghost-history.service now?'):run(['systemctl','restart','ghost-history.service'])
    if confirm('Enable ghost-history.service at boot?'):run(['systemctl','enable','ghost-history.service'])
    if confirm('Connect usage history to the original subscription page now?'):usage_attach()

def usage_attach():
    import getpass,socket,time,urllib.parse,urllib.request,urllib.error
    template=PANELS['1'][1]/'index.html'
    if template.is_symlink() or not template.is_file():print('Install the current 3X-UI Ghost template first.');return
    if subprocess.run(['systemctl','is-active','--quiet','ghost-history.service'],capture_output=True).returncode:
        print('Start the collector through option 3 first.');return
    destination=Path('/etc/ghost-gateway/config.json')
    candidate=json.loads(destination.read_text()) if destination.is_file() else {}
    if candidate and not candidate.get('status_only'):
        print('Use option 7 to attach the original subscription first, then retry option 8.');return
    if not candidate:
        source=getpass.getpass('ORIGINAL subscription URL (hidden): ').strip()
        u=module(ROOT/'status-monitor/subscription.py','subscription').validate_url(source)
        if u.scheme!='http':print('First connect the HTTPS data service through option 7, then retry option 8. No settings changed.');return
        port=int(input('Private-history data port [18090]: ').strip() or '18090')
        public_port=u.port or 80
        if port==public_port:raise ValueError('Choose a separate data port')
        authority=u.hostname if public_port==80 else u.hostname+':'+str(public_port)
        candidate={'listen_port':port,'upstream_port':public_port,'path_prefix':'/sub/','status_only':True,'allowed_origin':'http://'+authority}
        try:
            with socket.socket() as listener:listener.bind(('0.0.0.0',port))
        except OSError:print('Data port already occupied; nothing changed.');return
    candidate['history_enabled']=True;port=candidate['listen_port']
    m=module(ROOT/'scripts/status_attach.py','status_attach');original=template.read_text();updated=m.prepare_usage(original,port)
    gateway=module(ROOT/'gateway/server.py','gateway')
    with tempfile.TemporaryDirectory() as d:
        file=Path(d)/'config.json';file.write_text(json.dumps(candidate));gateway.config(file)
        print('Connect PRIVATE per-subscription usage history to the ORIGINAL 3X-UI subscription page.')
        print('The original URL/token, logo, reachability chart and panel credentials are preserved. 3X-UI restarts briefly.')
        if not confirm('Back up, connect usage chart and restart 3X-UI?'):return
        backup=Path(tempfile.mkdtemp(prefix='ghost-sub-backup.',dir='/root'));os.chmod(backup,0o700)
        shutil.copy2(template,backup/'index.html')
        if (template.parent/'manifest.json').is_file():shutil.copy2(template.parent/'manifest.json',backup/'manifest.json')
        (backup/'panel.json').write_text(json.dumps({'panel':'1','destination':str(template)}))
        old=destination.read_bytes() if destination.is_file() else None
        if old:(backup/'gateway-config.json').write_bytes(old)
        active=subprocess.run(['systemctl','is-active','--quiet','ghost-gateway.service'],capture_output=True).returncode==0
        if run(['bash',ROOT/'gateway/install.sh',file]):return
    changed=False
    try:
        if run(['systemctl','restart','ghost-gateway.service']):raise ValueError('Data service restart failed')
        ready=False
        for attempt in range(12):
            try:
                code,_=gateway.local_get(candidate,'/ghost-usage/aaaaaaaaaaaa')
                if code==404:ready=True;break
            except Exception:pass
            time.sleep(.25)
        if not ready:raise ValueError('History route not ready')
        m.write(template,updated);changed=True
        if run(['systemctl','restart','x-ui.service']):raise ValueError('Panel restart failed')
        if run(['systemctl','enable','ghost-gateway.service']):raise ValueError('Data service boot enable failed')
    except Exception:
        m.write(template,original)
        if old:destination.write_bytes(old);os.chmod(destination,0o640)
        if active:run(['systemctl','restart','ghost-gateway.service'])
        else:run(['systemctl','stop','ghost-gateway.service'])
        if changed:run(['systemctl','restart','x-ui.service'])
        print('Connection failed; template restored. Private backup: '+str(backup));return
    print('Usage chart attached. Open the ORIGINAL subscription and refresh without cache.')
    print('At least two successful samples are needed for a measured interval; collector interval is 15 minutes.')
    print('Only the history matching the subscription token is served; no user list is exposed. Backup: '+str(backup))

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
    print('Monitor targets configured. The chart can be attached to the original HTTP/HTTPS subscription link.')
    if confirm('Start/restart only ghost-status.service now?'):run(['systemctl','restart','ghost-status.service','ghost-gateway.service'])
    if confirm('Enable ghost-status.service at boot?'):run(['systemctl','enable','ghost-status.service','ghost-gateway.service'])
    if confirm('Connect the chart to the ORIGINAL subscription link now?'):gateway_setup()

def gateway_setup():
    import getpass,socket,urllib.parse,urllib.request
    source='';monitor=Path('/etc/ghost-status/config.json')
    if monitor.is_file():source=json.loads(monitor.read_text()).get('subscription_source','')
    if not source:source=getpass.getpass('ORIGINAL subscription URL (hidden): ').strip()
    importer=module(ROOT/'status-monitor/subscription.py','subscription');url=importer.validate_url(source)
    destination=Path('/etc/ghost-gateway/config.json');existing={}
    if destination.is_file():existing=json.loads(destination.read_text())
    # Migrate a previously pasted gateway URL back to its original subscription origin.
    if not existing.get('status_only') and url.port==existing.get('listen_port') and existing.get('upstream_port'):
        url=url._replace(netloc=url.hostname+':'+str(existing['upstream_port']))
    if existing.get('status_only') and url.port==existing.get('listen_port') and existing.get('allowed_origin'):
        url=url._replace(netloc=urllib.parse.urlsplit(existing['allowed_origin']).netloc)
    key,(name,folder)=panel();template=folder/'index.html'
    if template.is_symlink() or not template.is_file():print('Install the current Ghost Sub template for this panel first.');return
    port=int(input('Monitor data port ['+str(existing.get('listen_port',18090))+']: ').strip() or str(existing.get('listen_port',18090)))
    original_port=url.port or (443 if url.scheme=='https' else 80)
    if port==original_port:print('Monitor port must differ from the unchanged original subscription port.');return
    attach=module(ROOT/'scripts/status_attach.py','status_attach')
    original=template.read_text();updated=attach.prepare(original,port)
    origin=urllib.parse.urlunsplit((url.scheme,url.netloc,'','',''))
    candidate={'listen_port':port,'upstream_port':original_port,'path_prefix':'/sub/','status_only':True,'allowed_origin':origin,'history_enabled':bool(existing.get('history_enabled'))}
    if candidate.get('history_enabled') and key=='1':updated=attach.prepare_usage(updated,port)
    gateway=module(ROOT/'gateway/server.py','gateway')
    if url.scheme=='https':
        print('HTTPS data uses a separate port on the SAME subscription host. The original URL stays unchanged.')
        print('Provide an existing valid fullchain certificate and matching unencrypted key ON THIS SERVER.')
        print('Private TLS copies are stored for the data service; after certificate renewal, repeat option 7 with the renewed files.')
        cert=input('Fullchain PEM path ['+str(existing.get('tls_cert',''))+']: ').strip() or existing.get('tls_cert','')
        keyfile=input('Private key PEM path ['+str(existing.get('tls_key',''))+']: ').strip() or existing.get('tls_key','')
        candidate.update(tls_cert=cert,tls_key=keyfile)
        try:gateway.validate_certificate(candidate)
        except Exception:
            print('TLS files unavailable, mismatched, expiring, or not valid for this subscription host. No changes made.');return
    active=subprocess.run(['systemctl','is-active','--quiet','ghost-gateway.service'],capture_output=True).returncode==0
    with tempfile.TemporaryDirectory() as d:
        file=Path(d)/'config.json';file.write_text(json.dumps(candidate));gateway.config(file)
        if not (active and existing.get('listen_port')==port):
            try:
                with socket.socket() as listener:listener.bind(('0.0.0.0',port))
            except OSError:print('Monitor port already in use; choose another port. Nothing changed.');return
        print('Attach chart to the ORIGINAL '+name+' subscription. Original URL, port and token are retained.')
        print('Only the installed template and monitor data service change; no database/Apache/Nginx changes.')
        print('The old separate gateway page is disabled. The selected panel will restart briefly.')
        if not confirm('Save backup, connect monitor and restart selected panel?'):return
        backup=Path(tempfile.mkdtemp(prefix='ghost-sub-backup.',dir='/root'));os.chmod(backup,0o700)
        shutil.copy2(template,backup/'index.html')
        (backup/'panel.json').write_text(json.dumps({'panel':key,'destination':str(template)}))
        if (folder/'manifest.json').is_file():shutil.copy2(folder/'manifest.json',backup/'manifest.json')
        old_config=destination.read_bytes() if destination.is_file() else None
        if old_config:(backup/'gateway-config.json').write_bytes(old_config)
        if run(['bash',ROOT/'gateway/install.sh',file]):return
    try:
        if run(['systemctl','restart','ghost-gateway.service']):raise ValueError('Monitor restart failed')
        import time
        ready=False
        for attempt in range(12):
            try:
                code,body=gateway.local_get(candidate,'/ghost-status.json')
                feed=json.loads(body)
                ready=code==200 and feed.get('schema')==1 and isinstance(feed.get('nodes'),dict)
                if ready:break
            except Exception:pass
            time.sleep(.25)
        if not ready:raise ValueError('Monitor feed unavailable')
        attach.write(template,updated)
        if key=='1':restart=['systemctl','restart','x-ui.service']
        elif key=='2':restart=['pasarguard','restart']
        elif subprocess.run(['systemctl','is-active','--quiet','marzban'],capture_output=True).returncode==0:restart=['systemctl','restart','marzban']
        else:restart=['marzban','restart']
        if run(restart):raise ValueError('Panel restart failed')
        if run(['systemctl','enable','ghost-gateway.service']):raise ValueError('Monitor boot enable failed')
    except Exception:
        attach.write(template,original)
        if old_config:destination.write_bytes(old_config);os.chmod(destination,0o640)
        if active:run(['systemctl','restart','ghost-gateway.service'])
        else:run(['systemctl','stop','ghost-gateway.service'])
        if 'restart' in locals():run(restart)
        print('Setup failed; template restored. Private backup: '+str(backup));return
    print('Connected. Open your ORIGINAL subscription URL, then refresh without cache. No new subscription link is needed.')
    print('If needed, allow TCP '+str(port)+' through the existing firewall for monitor JSON only. Backup: '+str(backup))

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
        print('\nGhost Sub Manager\n1) Install/apply bundled template version\n2) Change brand/logo/default theme (installer)\n3) Configure 3X-UI usage history\n4) Configure server reachability monitor\n5) Read-only installation checks\n6) Restore matching template backup\n7) Attach chart to ORIGINAL subscription (keep URL)\n8) Attach 3X-UI usage chart to ORIGINAL subscription\n0) Exit')
        try:
            choice=input('Select: ').strip()
            if choice=='0':return
            if choice=='5':diagnostics();continue
            if choice not in ('1','2','3','4','6','7','8'):print('Invalid selection');continue
            if not root_terminal():continue
            if choice in ('1','2'):run(['bash',ROOT/'scripts/install_template.sh'])
            elif choice=='3':history_setup()
            elif choice=='4':status_setup()
            elif choice=='6':rollback()
            elif choice=='7':gateway_setup()
            elif choice=='8':usage_attach()
        except (EOFError,KeyboardInterrupt):print('\nClosed.');return
        except (OSError,ValueError):print('Operation could not complete; no credentials are printed. Review configuration privately.')
if __name__=='__main__':main()
