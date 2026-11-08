#!/usr/bin/env bash
# Optional installation only. No panel API is contacted and no service is started here.
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Root required'; exit 1; }
[[ $# == 1 ]] || { echo 'Usage: bash traffic-history/install.sh CONFIG_JSON'; exit 2; }
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
command -v python3 >/dev/null
python3 -I - "$source_dir" "$1" <<'PY'
import importlib.util,sys
spec=importlib.util.spec_from_file_location('ghost_status',sys.argv[1]+'/history.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.load_config(sys.argv[2]);print('Offline history configuration: OK; no probes executed')
PY
for file in /opt/ghost-history /opt/ghost-history/history.py /etc/ghost-history /etc/ghost-history/config.json /etc/systemd/system/ghost-history.service; do
  [[ ! -L "$file" ]] || { echo 'Refusing symlink destination'; exit 1; }
done
if [[ -e /etc/ghost-history/config.json ]]; then
  echo 'Existing history config found; retained. Review it before service start.'
fi
if ! id ghost-history >/dev/null 2>&1; then
  useradd --system --user-group --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin ghost-history
fi
install -d -m 755 /opt/ghost-history
install -d -m 750 -o root -g ghost-history /etc/ghost-history
if [[ ! -f /etc/ghost-history/config.json ]]; then
  install -m 640 -o root -g ghost-history "$1" /etc/ghost-history/config.json
fi
backup=$(mktemp -d /root/ghost-history-backup.XXXXXX)
[[ ! -f /opt/ghost-history/history.py ]] || cp -p /opt/ghost-history/history.py "$backup/history.py"
[[ ! -f /etc/systemd/system/ghost-history.service ]] || cp -p /etc/systemd/system/ghost-history.service "$backup/ghost-history.service"
install -m 644 "$source_dir/history.py" /opt/ghost-history/history.py
install -m 644 "$source_dir/ghost-history.service" /etc/systemd/system/ghost-history.service
systemctl daemon-reload
printf 'Installed; no service started/restarted/enabled. Backup: %s\n' "$backup"
echo 'Next, review config, then explicitly run: systemctl start ghost-history.service'
echo 'Publish /history/ only through the protected subscription-token route; see docs/3XUI_HISTORY_FA.md.'
