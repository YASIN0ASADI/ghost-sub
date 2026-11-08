#!/usr/bin/env bash
# Ghost Sub — visual refresh installer. Usage Tracker flow retained below.
set -euo pipefail
BASE_URL="https://raw.githubusercontent.com/YASIN0ASADI/ghost-sub/main"
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; BLD='\033[1m'; DIM='\033[2m'; RST='\033[0m'
[[ $EUID == 0 ]] || { echo 'Run as root: sudo bash install.sh'; exit 1; }
for cmd in curl python3; do
  command -v "$cmd" >/dev/null || { echo "Missing dependency: $cmd. Install it first."; exit 1; }
done
printf '\nGhost Sub — Appearance setup\n\n1) 3X-UI\n2) Pasarguard\n3) Marzban\n'
read -rp 'Panel [1/2/3]: ' PANEL_CHOICE
case "$PANEL_CHOICE" in
  1) PANEL_NAME='3X-UI'; TEMPLATE='sub.html'; INSTALL_DIR='/etc/3x-ui/sub_templates/my-theme';;
  2) PANEL_NAME='Pasarguard'; TEMPLATE='pasarguard.html'; INSTALL_DIR='/var/lib/pasarguard/templates/subscription';;
  3) PANEL_NAME='Marzban'; TEMPLATE='marzban.html'; INSTALL_DIR='/var/lib/marzban/templates/subscription';;
  *) echo 'Invalid panel; nothing changed'; exit 1;;
esac
OUTPUT_FILE="$INSTALL_DIR/index.html"
echo 'Existing refresh-version branding can be kept by pressing Enter.'
echo 'For an older installation, enter its brand again on the first update.'
read -rp 'Brand name (Enter: keep saved): ' BRAND_NAME
read -rp 'Default theme [1 red / 2 green / 3 blue; Enter: keep saved or red]: ' THEME_CHOICE
case "$THEME_CHOICE" in
  '') THEME_NAME='';; 1) THEME_NAME='red';; 2) THEME_NAME='green';; 3) THEME_NAME='blue';;
  *) echo 'Invalid theme; nothing changed'; exit 1;;
esac
echo 'Profile image: paste a PNG/JPG/WebP path ON THIS SERVER or an HTTPS image URL.'
echo 'Example: /root/logo.jpg or https://your-domain.example/logo.png'
echo 'Windows C:\ paths must be uploaded to the server first.'
echo 'Or choose: 1) Ghost  2) Enter image address  3) No image'
read -rp 'Image address or choice [Enter: keep saved / default Ghost]: ' LOGO_CHOICE
LOGO_SOURCE=''
SHAPE_ARGS=()
case "$LOGO_CHOICE" in
  '') LOGO_MODE='keep';; 1|ghost) LOGO_MODE='ghost';; 3|none) LOGO_MODE='none';;
  2) LOGO_MODE='custom'; read -rp 'Image path on server or HTTPS URL: ' LOGO_SOURCE;;
  *) LOGO_MODE='custom'; LOGO_SOURCE="$LOGO_CHOICE";;
esac
if [[ "$LOGO_MODE" == custom ]]; then
 read -rp 'Profile frame: 1) Round  2) Rounded square [default 1]: ' LOGO_SHAPE
 case "$LOGO_SHAPE" in
  ''|1) SHAPE_ARGS=(--logo-shape circle);;
  2) SHAPE_ARGS=(--logo-shape square);;
  *) echo 'Invalid frame choice; nothing changed'; exit 1;;
 esac
fi
echo 'Next section is SERVER MONITORING, not an image address.'
echo 'Optional measured server status: enter the public JSON feed path/HTTPS URL.'
echo 'Enter keeps saved settings; type off to disable. No feed means Unknown.'
read -rp 'Status feed [e.g. /ghost-status.json]: ' STATUS_FEED
STATUS_ARGS=()
if [[ "$STATUS_FEED" == off ]]; then STATUS_ARGS=(--status-feed '');
elif [[ -n "$STATUS_FEED" ]]; then STATUS_ARGS=(--status-feed "$STATUS_FEED"); fi
USAGE_ARGS=()
if [[ "$PANEL_CHOICE" == 1 ]]; then
 echo 'Optional 3X-UI usage history (separate collector required).'
 read -rp 'History route [e.g. /ghost-usage/; Enter keep / off disable]: ' USAGE_BASE
 if [[ "$USAGE_BASE" == off ]]; then USAGE_ARGS=(--usage-base '');
 elif [[ -n "$USAGE_BASE" ]]; then USAGE_ARGS=(--usage-base "$USAGE_BASE"); fi
fi
echo "Panel: $PANEL_NAME | Destination: $OUTPUT_FILE"
echo 'The existing template/manifest will be backed up. Tracker settings remain separate.'
read -rp 'Install and restart selected panel? [y/N]: ' CONFIRM
[[ "$CONFIRM" =~ ^[Yy]$ ]] || { echo 'Cancelled'; exit 0; }
TMP_WORK=$(mktemp -d)
trap 'rm -rf -- "$TMP_WORK"' EXIT
get_source() {
  local path=$1 destination=$2
  if [[ -f "$SCRIPT_DIR/$path" ]]; then cp -- "$SCRIPT_DIR/$path" "$destination";
  else curl --fail --silent --show-error --location --proto '=https' --proto-redir '=https' "$BASE_URL/$path" -o "$destination"; fi
}
get_source "$TEMPLATE" "$TMP_WORK/template.html"
get_source scripts/branding.py "$TMP_WORK/branding.py"
python3 -I "$TMP_WORK/branding.py" --template "$TMP_WORK/template.html" \
  --output "$TMP_WORK/index.html" --previous "$OUTPUT_FILE" \
  --brand "$BRAND_NAME" --theme "$THEME_NAME" --logo-mode "$LOGO_MODE" \
  --logo-source "$LOGO_SOURCE" --manifest "$TMP_WORK/manifest.json" "${STATUS_ARGS[@]}" "${USAGE_ARGS[@]}" "${SHAPE_ARGS[@]}"
# Preparation above does not overwrite existing template or panel settings.
[[ ! -L "$INSTALL_DIR" && ! -L "$OUTPUT_FILE" && ! -L "$INSTALL_DIR/manifest.json" ]] || { echo 'Refusing symlink destination'; exit 1; }
mkdir -p -- "$INSTALL_DIR"
if [[ -e "$OUTPUT_FILE" || -e "$INSTALL_DIR/manifest.json" ]]; then
  PRIVATE_BACKUP=$(mktemp -d /root/ghost-sub-backup.XXXXXX)
  [[ ! -f "$OUTPUT_FILE" ]] || cp -p -- "$OUTPUT_FILE" "$PRIVATE_BACKUP/index.html"
  [[ ! -f "$INSTALL_DIR/manifest.json" ]] || cp -p -- "$INSTALL_DIR/manifest.json" "$PRIVATE_BACKUP/manifest.json"
  python3 -I - "$PRIVATE_BACKUP/panel.json" "$PANEL_CHOICE" "$OUTPUT_FILE" <<'PYMETA'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);p.write_text(json.dumps({'panel':sys.argv[2],'destination':sys.argv[3]}));p.chmod(0o600)
PYMETA
  echo "Private backup: $PRIVATE_BACKUP"
fi
install -m 644 "$TMP_WORK/index.html" "$OUTPUT_FILE"
install -m 644 "$TMP_WORK/manifest.json" "$INSTALL_DIR/manifest.json"
BRAND_UPPER="$BRAND_NAME"
echo 'Appearance installed. Brand, logo and theme are stored in the template for the next update.'

# ── Restart panel ────────────────────────────────────────────────
echo ""
echo -e "  Reloading ${PANEL_NAME}..."
case "$PANEL_CHOICE" in
  1)
    if systemctl is-active --quiet x-ui 2>/dev/null; then
      systemctl restart x-ui \
        && echo -e "    ${GRN}✓ x-ui restarted${RST}" \
        || echo -e "    ${YLW}⚠  Restart manually: systemctl restart x-ui${RST}"
    else
      echo -e "    ${YLW}⚠  Restart manually: systemctl restart x-ui${RST}"
    fi
    ;;
  2)
    if command -v pasarguard &>/dev/null; then
      pasarguard restart \
        && echo -e "    ${GRN}✓ Pasarguard restarted${RST}" \
        || echo -e "    ${YLW}⚠  Restart manually: pasarguard restart${RST}"
    else
      echo -e "    ${YLW}⚠  Restart manually: pasarguard restart${RST}"
    fi
    ;;
  3)
    if systemctl is-active --quiet marzban 2>/dev/null; then
      systemctl restart marzban \
        && echo -e "    ${GRN}✓ Marzban restarted${RST}" \
        || echo -e "    ${YLW}⚠  Restart manually: systemctl restart marzban${RST}"
    elif command -v marzban &>/dev/null; then
      marzban restart \
        && echo -e "    ${GRN}✓ Marzban restarted${RST}" \
        || echo -e "    ${YLW}⚠  Restart manually: marzban restart${RST}"
    else
      echo -e "    ${YLW}⚠  Restart manually: systemctl restart marzban${RST}"
    fi
    ;;
esac

# ── Done ─────────────────────────────────────────────────────────
echo ""
echo -e "${GRN}╔══════════════════════════════════════════════════════════╗${RST}"
echo -e "${GRN}║   ✓  Done! Ghost Sub installed successfully.             ║${RST}"
echo -e "${GRN}╚══════════════════════════════════════════════════════════╝${RST}"
echo ""
echo -e "  Brand: ${GRN}${BRAND_UPPER}${RST}   Theme: ${GRN}${THEME_NAME}${RST}"
echo ""

case "$PANEL_CHOICE" in
  1)
    echo -e "  ${BLD}Activate in 3X-UI panel:${RST}"
    echo -e "  ${YLW}Panel Settings → Subscription → Subscription Template Path${RST}"
    echo -e "  Enter: ${YLW}/etc/3x-ui/sub_templates/my-theme/${RST}"
    ;;
  2)
    echo -e "  ${BLD}Activate in Pasarguard (.env):${RST}"
    echo -e "  ${YLW}CUSTOM_TEMPLATES_DIRECTORY=\"/var/lib/pasarguard/templates/\"${RST}"
    echo -e "  ${YLW}SUBSCRIPTION_PAGE_TEMPLATE=\"subscription/index.html\"${RST}"
    echo -e "  ${YLW}Disable Subscription Template → OFF in panel settings${RST}"
    ;;
  3)
    echo -e "  ${BLD}Activate in Marzban (.env):${RST}"
    echo -e "  ${YLW}CUSTOM_TEMPLATES_DIRECTORY=\"/var/lib/marzban/templates/\"${RST}"
    echo -e "  ${YLW}SUBSCRIPTION_PAGE_TEMPLATE=\"subscription/index.html\"${RST}"
    ;;
esac
echo ""

# ── Optional: Usage Chart Tracker (Pasarguard / Marzban) ───────────
if [[ "$PANEL_CHOICE" == "2" || "$PANEL_CHOICE" == "3" ]]; then
  TRACKER_DIR="/opt/ghost-tracker"
  TRACKER_CONFIG="$TRACKER_DIR/tracker_config.json"

  echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
  echo -e "  ${BLD}📊 نمودار مصرف واقعی${RST}"
  echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"

  if [[ -f "$TRACKER_CONFIG" ]]; then
    # ── Tracker از قبل نصب شده — فقط بپرس آپدیت بشه یا نه ─────────
    echo -e "  ${GRN}✓ Usage Tracker قبلاً نصب شده.${RST}"
    echo -e "  ${DIM}اطلاعات پنل ذخیره‌شده، دیگه نیازی به وارد کردن دوباره نیست.${RST}"
    echo ""
    read -rp "  ➤ آپدیت به آخرین نسخه Tracker؟ [Y/n]: " UPDATE_TRACKER
    UPDATE_TRACKER="${UPDATE_TRACKER:-Y}"

    if [[ "$UPDATE_TRACKER" =~ ^[Yy]$ ]]; then
      echo ""
      echo -e "${BLD}Updating Usage Tracker...${RST}"

      if curl -fsSL "$BASE_URL/tracker/tracker.py" -o "$TRACKER_DIR/tracker.py"; then
        echo -e "    ${GRN}✓ tracker.py updated${RST}"
      else
        echo -e "    ${RED}✗ Failed to download tracker.py${RST}"
      fi

      if curl -fsSL "$BASE_URL/tracker/ghost-tracker.service" -o /etc/systemd/system/ghost-tracker.service; then
        systemctl daemon-reload
        echo -e "    ${GRN}✓ service file updated${RST}"
      fi

      systemctl restart ghost-tracker &>/dev/null \
        && echo -e "    ${GRN}✓ ghost-tracker restarted${RST}" \
        || echo -e "    ${YLW}⚠  Restart manually: systemctl restart ghost-tracker${RST}"

      echo ""
      echo -e "  ${GRN}✓ Tracker به‌روزرسانی شد.${RST}"
    else
      echo -e "  ${DIM}Tracker دست‌نخورده باقی موند.${RST}"
    fi

  else
    # ── نصب اول — اطلاعات پنل رو بپرس ────────────────────────────
    echo -e "  ${DIM}یه سرویس کوچیک نصب میشه که هر چند دقیقه مصرف کاربرا رو از${RST}"
    echo -e "  ${DIM}API پنل می‌خونه و نمودار واقعی مصرف رو تو صفحه ساب می‌سازه.${RST}"
    echo ""
    read -rp "  ➤ نصب Usage Tracker؟ [y/N]: " INSTALL_TRACKER
    INSTALL_TRACKER=$(echo "$INSTALL_TRACKER" | xargs)

    if [[ "$INSTALL_TRACKER" =~ ^[Yy]$ ]]; then
      echo ""
      echo -e "  ${BLD}Panel URL${RST}  ${YLW}(e.g: https://panel.example.com:8000)${RST}"
      read -rp "  ➤ URL: " TRACKER_PANEL_URL
      TRACKER_PANEL_URL=$(echo "$TRACKER_PANEL_URL" | xargs)

      echo -e "  ${BLD}Admin username${RST}"
      read -rp "  ➤ Username: " TRACKER_ADMIN_USER
      TRACKER_ADMIN_USER=$(echo "$TRACKER_ADMIN_USER" | xargs)

      echo -e "  ${BLD}Admin password${RST}"
      read -rsp "  ➤ Password: " TRACKER_ADMIN_PASS
      echo ""

      if [[ "$PANEL_CHOICE" == "2" ]]; then
        TRACKER_PANEL_TYPE="pasarguard"
      else
        TRACKER_PANEL_TYPE="marzban"
      fi

      if [[ -n "$TRACKER_PANEL_URL" && -n "$TRACKER_ADMIN_USER" && -n "$TRACKER_ADMIN_PASS" ]]; then
        echo ""
        echo -e "${BLD}Installing Usage Tracker...${RST}"

        mkdir -p "$TRACKER_DIR"

        # دانلود tracker.py
        if curl -fsSL "$BASE_URL/tracker/tracker.py" -o "$TRACKER_DIR/tracker.py"; then
          echo -e "    ${GRN}✓ tracker.py downloaded${RST}"
        else
          echo -e "    ${RED}✗ Failed to download tracker.py${RST}"
        fi

        # ساخت فایل کانفیگ
        cat > "$TRACKER_CONFIG" << CFGEOF
{
  "panel_type": "${TRACKER_PANEL_TYPE}",
  "panel_url": "${TRACKER_PANEL_URL}",
  "admin_username": "${TRACKER_ADMIN_USER}",
  "admin_password": "${TRACKER_ADMIN_PASS}",
  "output_dir": "$(dirname "$OUTPUT_FILE")",
  "interval_minutes": 15,
  "verify_ssl": true
}
CFGEOF
        chmod 600 "$TRACKER_CONFIG"
        echo -e "    ${GRN}✓ config saved (panel: ${TRACKER_PANEL_TYPE})${RST}"

        # نصب httpx
        pip3 install httpx --break-system-packages -q 2>/dev/null \
          || pip3 install httpx -q 2>/dev/null \
          || echo -e "    ${YLW}⚠  Install manually: pip3 install httpx --break-system-packages${RST}"
        echo -e "    ${GRN}✓ dependencies installed${RST}"

        # دانلود و فعال‌سازی systemd service
        if curl -fsSL "$BASE_URL/tracker/ghost-tracker.service" -o /etc/systemd/system/ghost-tracker.service; then
          systemctl daemon-reload
          systemctl enable ghost-tracker --now &>/dev/null \
            && echo -e "    ${GRN}✓ ghost-tracker service started${RST}" \
            || echo -e "    ${YLW}⚠  Start manually: systemctl start ghost-tracker${RST}"
        else
          echo -e "    ${RED}✗ Failed to download service file${RST}"
        fi

        echo ""
        echo -e "  ${GRN}✓ Usage Tracker installed.${RST} ${DIM}اولین داده‌ها تا ۱۵ دقیقه دیگه آماده میشه.${RST}"
        echo -e "  ${DIM}Logs: journalctl -u ghost-tracker -f${RST}"
      else
        echo -e "  ${YLW}⚠  اطلاعات ناقص بود — Tracker نصب نشد. بعداً می‌تونی دستی نصبش کنی.${RST}"
      fi
    fi
  fi
  echo ""
fi


