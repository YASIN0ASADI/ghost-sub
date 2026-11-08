#!/usr/bin/env bash
# Optional installation only. No target is checked and no service is started here.
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Root required'; exit 1; }
[[ $# == 1 ]] || { echo 'Usage: bash status-monitor/install.sh CONFIG_JSON'; exit 2; }
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
command -v python3 >/dev/null
python3 -I - "$source_dir" "$1" <<'PY'
import importlib.util,sys
spec=importlib.util.spec_from_file_location('ghost_status',sys.argv[1]+'/monitor.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.config(sys.argv[2]);print('Offline monitor configuration: OK; no probes executed')
PY
for file in /opt/ghost-status /opt/ghost-status/monitor.py /opt/ghost-status/subscription.py /etc/ghost-status /etc/ghost-status/config.json /etc/systemd/system/ghost-status.service; do
  [[ ! -L "$file" ]] || { echo 'Refusing symlink destination'; exit 1; }
done
if [[ -e /etc/ghost-status/config.json ]]; then
  echo 'Existing monitor config found; retained. Review it before service start.'
fi
if ! id ghost-status >/dev/null 2>&1; then
  useradd --system --user-group --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin ghost-status
fi
install -d -m 755 /opt/ghost-status
install -d -m 750 -o root -g ghost-status /etc/ghost-status
if [[ ! -f /etc/ghost-status/config.json ]]; then
  install -m 640 -o root -g ghost-status "$1" /etc/ghost-status/config.json
fi
backup=$(mktemp -d /root/ghost-status-backup.XXXXXX)
[[ ! -f /opt/ghost-status/monitor.py ]] || cp -p /opt/ghost-status/monitor.py "$backup/monitor.py"
[[ ! -f /etc/systemd/system/ghost-status.service ]] || cp -p /etc/systemd/system/ghost-status.service "$backup/ghost-status.service"
install -m 644 "$source_dir/monitor.py" /opt/ghost-status/monitor.py
install -m 644 "$source_dir/subscription.py" /opt/ghost-status/subscription.py
install -m 644 "$source_dir/ghost-status.service" /etc/systemd/system/ghost-status.service
systemctl daemon-reload
printf 'Installed; no service started/restarted/enabled. Backup: %s\n' "$backup"
echo 'Next, review config, then explicitly run: systemctl start ghost-status.service'
echo 'Publish only /status.json through an HTTPS reverse proxy; see docs/STATUS_MONITOR_FA.md.'
