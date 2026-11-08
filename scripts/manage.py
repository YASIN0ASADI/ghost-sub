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

def confirm(text):return input(text+' Type YES: ').strip()=='YES'

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
    for unit in ['ghost-tracker.service','ghost-history.service','ghost-status.service']:
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
    config=Path('/etc/ghost-status/config.json')
    if not config.exists():
        print('Fixed TCP targets only. No browser-side scanning.')
        probe=input('Probe location label: ').strip() or 'Monitoring server';targets=[]
        while len(targets)<64:
            host=input('Node host (Enter to finish): ').strip()
            if not host:break
            targets.append({'host':host,'port':int(input('Node TCP port: ')),'country':input('Country ISO2 (optional): ').strip().upper()})
        candidate={'probe_label':probe,'interval_seconds':60,'timeout_seconds':3,'listen_port':19191,'targets':targets}
        m=module(ROOT/'status-monitor/monitor.py','monitor')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'config.json';p.write_text(json.dumps(candidate));m.config(p)
            if not confirm('Save config and install monitor (no automatic start)?'):return
            if run(['bash',ROOT/'status-monitor/install.sh',p]):return
    else:
        if not confirm('Retain existing config and install/update monitor files?'):return
        if run(['bash',ROOT/'status-monitor/install.sh',config]):return
    print('Publish only /status.json through the intended HTTPS subscription origin; set the feed in template appearance setup.')
    if confirm('Start/restart only ghost-status.service now?'):run(['systemctl','restart','ghost-status.service'])
    if confirm('Enable ghost-status.service at boot?'):run(['systemctl','enable','ghost-status.service'])

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
        print('\nGhost Sub Manager\n1) Install/apply bundled template version\n2) Change brand/logo/default theme (installer)\n3) Configure 3X-UI usage history\n4) Configure server reachability monitor\n5) Read-only installation checks\n6) Restore matching template backup\n0) Exit')
        try:
            choice=input('Select: ').strip()
            if choice=='0':return
            if choice=='5':diagnostics();continue
            if choice not in ('1','2','3','4','6'):print('Invalid selection');continue
            if not root_terminal():continue
            if choice in ('1','2'):run(['bash',ROOT/'install.sh'])
            elif choice=='3':history_setup()
            elif choice=='4':status_setup()
            elif choice=='6':rollback()
        except (EOFError,KeyboardInterrupt):print('\nClosed.');return
        except (OSError,ValueError):print('Operation could not complete; no credentials are printed. Review configuration privately.')
if __name__=='__main__':main()
