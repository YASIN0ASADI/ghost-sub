#!/usr/bin/env python3
"""Install the bundled manager and known sources only; no account/network/service changes."""
import argparse,os,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
FILES=['install.sh','scripts/install_template.sh','scripts/status_attach.py','scripts/status_ui.js','sub.html','marzban.html','pasarguard.html','manifest.json','scripts/branding.py','scripts/manage.py','scripts/install_manager.py','tracker/tracker.py','tracker/ghost-tracker.service','traffic-history/history.py','traffic-history/install.sh','traffic-history/ghost-history.service','status-monitor/monitor.py','status-monitor/subscription.py','status-monitor/install.sh','status-monitor/ghost-status.service','gateway/server.py','gateway/install.sh','gateway/ghost-gateway.service']

def install(prefix):
    prefix=Path(prefix)
    for rel in FILES:
        source=ROOT/rel
        if not source.is_file() or source.is_symlink():raise ValueError('Missing trusted source: '+rel)
    payloads=[(prefix/'opt/ghost-sub-manager'/rel,(ROOT/rel).read_bytes(),0o644) for rel in FILES]
    payloads.append((prefix/'usr/local/bin/ghost-sub',b'#!/bin/sh\nexec /usr/bin/python3 -I /opt/ghost-sub-manager/scripts/manage.py "$@"\n',0o755))
    for path,_,_ in payloads:
        for parent in [path,*path.parents]:
            if parent==prefix:break
            if parent.is_symlink():raise ValueError('Symlink destination refused')
    for path,data,mode in payloads:
        missing=[];parent=path.parent
        while not parent.exists():missing.append(parent);parent=parent.parent
        for parent in reversed(missing):parent.mkdir(mode=0o755);parent.chmod(0o755)
        fd,temp=tempfile.mkstemp(prefix='.ghost-manager-',dir=path.parent)
        try:
            with os.fdopen(fd,'wb') as f:f.write(data)
            os.chmod(temp,mode);os.replace(temp,path)
        finally:
            if os.path.exists(temp):os.unlink(temp)
    print('Manager files installed; command: ghost-sub. No service started or enabled.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--staging-dir');a=p.parse_args()
    if a.staging_dir:
        path=Path(a.staging_dir)
        if not path.is_absolute() or path.exists():raise SystemExit('Staging directory must be new and absolute')
        path.mkdir(mode=0o700);install(path)
    else:
        if os.geteuid()!=0:raise SystemExit('Root required')
        install(Path('/'))
if __name__=='__main__':main()
