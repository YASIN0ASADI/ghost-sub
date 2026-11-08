#!/usr/bin/env bash
# Ghost Sub one-command bootstrap and terminal menu.
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run this installer as root.'; exit 1; }
for cmd in curl python3; do
  command -v "$cmd" >/dev/null || { echo "Missing dependency: $cmd"; exit 1; }
done
stage=$(mktemp -d)
trap 'rm -rf -- "$stage"' EXIT
printf '\nGhost Sub — downloading the complete management menu...\n'
curl --fail --silent --show-error --location --retry 2 \
  --proto '=https' --proto-redir '=https' --connect-timeout 20 --max-time 180 \
  https://codeload.github.com/YASIN0ASADI/ghost-sub/tar.gz/refs/heads/main \
  -o "$stage/source.tar.gz"
python3 -I - "$stage/source.tar.gz" "$stage/source" <<'PYBOOT'
import pathlib,sys,tarfile
files=['install.sh', 'scripts/install_template.sh', 'sub.html', 'marzban.html', 'pasarguard.html', 'manifest.json', 'scripts/branding.py', 'scripts/manage.py', 'scripts/install_manager.py', 'tracker/tracker.py', 'tracker/ghost-tracker.service', 'traffic-history/history.py', 'traffic-history/install.sh', 'traffic-history/ghost-history.service', 'status-monitor/monitor.py','status-monitor/subscription.py', 'status-monitor/install.sh', 'status-monitor/ghost-status.service']
base=pathlib.Path(sys.argv[2]);base.mkdir(mode=0o700)
with tarfile.open(sys.argv[1],'r:gz') as archive:
    pending=[]
    for rel in files:
        member=archive.getmember('ghost-sub-main/'+rel)
        if not member.isfile() or member.size>8*1024*1024:
            raise SystemExit('Invalid installer file: '+rel)
        pending.append((rel,archive.extractfile(member).read()))
    if sum(len(data) for _,data in pending)>32*1024*1024:
        raise SystemExit('Installer source too large')
    for rel,data in pending:
        path=base/rel;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
PYBOOT
python3 -I "$stage/source/scripts/install_manager.py"
rm -rf -- "$stage"
trap - EXIT
exec python3 -I /opt/ghost-sub-manager/scripts/manage.py
