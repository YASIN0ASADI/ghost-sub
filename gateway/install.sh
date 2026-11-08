#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 && $# == 1 ]] || { echo 'Root and one config path required'; exit 1; }
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 -I - "$source_dir" "$1" <<'PY'
import importlib.util,sys
spec=importlib.util.spec_from_file_location('gateway',sys.argv[1]+'/server.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.config(sys.argv[2]);print('Offline gateway config: OK')
PY
for path in /opt/ghost-gateway /opt/ghost-gateway/server.py /etc/ghost-gateway /etc/ghost-gateway/config.json /etc/systemd/system/ghost-gateway.service; do
 [[ ! -L "$path" ]] || { echo 'Symlink destination refused'; exit 1; }
done
id ghost-gateway >/dev/null 2>&1 || useradd --system --user-group --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin ghost-gateway
backup=$(mktemp -d /root/ghost-gateway-backup.XXXXXX)
for path in /opt/ghost-gateway/server.py /etc/ghost-gateway/config.json /etc/systemd/system/ghost-gateway.service; do
 [[ ! -f "$path" ]] || cp -p "$path" "$backup/$(basename -- "$path")"
done
install -d -m 755 /opt/ghost-gateway
install -d -m 750 -o root -g ghost-gateway /etc/ghost-gateway
install -m 640 -o root -g ghost-gateway "$1" /etc/ghost-gateway/config.json
install -m 644 "$source_dir/server.py" /opt/ghost-gateway/server.py
install -m 644 "$source_dir/ghost-gateway.service" /etc/systemd/system/ghost-gateway.service
systemctl daemon-reload
printf 'Gateway files installed. No start/enable. Backup: %s\n' "$backup"
