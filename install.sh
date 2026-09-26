#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║          Ghost Sub — Universal Installer                     ║
# ║          github.com/YASIN0ASADI/ghost-sub                   ║
# ╚══════════════════════════════════════════════════════════════╝

set -e

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
CYN='\033[0;36m'
PRP='\033[0;35m'
BLD='\033[1m'
DIM='\033[2m'
RST='\033[0m'

BASE_URL="https://raw.githubusercontent.com/YASIN0ASADI/ghost-sub/main"

clear
echo ""
echo -e "${CYN}╔══════════════════════════════════════════════════════════╗${RST}"
echo -e "${CYN}║${RST}    👻  ${BLD}Ghost Sub — Universal Installer${RST}                ${CYN}║${RST}"
echo -e "${CYN}║${RST}         github.com/YASIN0ASADI/ghost-sub               ${CYN}║${RST}"
echo -e "${CYN}╚══════════════════════════════════════════════════════════╝${RST}"
echo ""

# ── Root check ──────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}[✗] Run as root:  sudo bash install.sh${RST}"
  exit 1
fi

for cmd in curl sed; do
  command -v "$cmd" &>/dev/null || apt-get install -y "$cmd" -qq 2>/dev/null || true
done

# ── Panel selection ─────────────────────────────────────────────
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "  ${BLD}Select your panel:${RST}"
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo ""
echo -e "  ${BLD}1)${RST} 3X-UI"
echo -e "  ${BLD}2)${RST} Pasarguard"
echo -e "  ${BLD}3)${RST} Marzban"
echo ""

while true; do
  read -rp "  ➤ Enter 1, 2 or 3: " PANEL_CHOICE
  PANEL_CHOICE=$(echo "$PANEL_CHOICE" | xargs)
  [[ "$PANEL_CHOICE" =~ ^[123]$ ]] && break
  echo -e "  ${RED}[✗] Please enter 1, 2 or 3.${RST}"
done

echo ""

# ── Theme selection ─────────────────────────────────────────────
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "  ${BLD}Select your default theme:${RST}"
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo ""
echo -e "  ${RED}${BLD}1)${RST} ${RED}Red${RST}         (پیش‌فرض قرمز)"
echo -e "  ${GRN}${BLD}2)${RST} ${GRN}Green${RST}       (پیش‌فرض سبز)"
echo -e "  ${PRP}${BLD}3)${RST} ${PRP}Blue/Purple${RST} (پیش‌فرض آبی-بنفش)"
echo ""
echo -e "  ${DIM}(کاربر می‌تونه بعداً توی خود صفحه تم رو عوض کنه)${RST}"
echo ""

while true; do
  read -rp "  ➤ Enter 1, 2 or 3: " THEME_CHOICE
  THEME_CHOICE=$(echo "$THEME_CHOICE" | xargs)
  [[ "$THEME_CHOICE" =~ ^[123]$ ]] && break
  echo -e "  ${RED}[✗] Please enter 1, 2 or 3.${RST}"
done

case "$THEME_CHOICE" in
  1) THEME_NAME="red";   THEME_CLASS="" ;;
  2) THEME_NAME="green"; THEME_CLASS="theme-green" ;;
  3) THEME_NAME="blue";  THEME_CLASS="theme-blue" ;;
esac

echo ""

# ── Branding info ───────────────────────────────────────────────
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "  ${BLD}Enter your branding info:${RST}"
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo ""

while true; do
  echo -e "  ${BLD}Brand / Service Name${RST}  ${YLW}(e.g: DARK VPN, PHANTOM, GHOST NET)${RST}"
  read -rp "  ➤ Brand name: " BRAND_NAME
  BRAND_NAME=$(echo "$BRAND_NAME" | xargs)
  [[ -n "$BRAND_NAME" ]] && break
  echo -e "  ${RED}[✗] Cannot be empty.${RST}"
done

BRAND_UPPER=$(echo "$BRAND_NAME" | tr '[:lower:]' '[:upper:]')

# ── Set paths based on panel ────────────────────────────────────
case "$PANEL_CHOICE" in
  1)
    PANEL_NAME="3X-UI"
    REPO_RAW="$BASE_URL/sub.html"
    INSTALL_DIR="/etc/3x-ui/sub_templates/my-theme"
    OUTPUT_FILE="$INSTALL_DIR/index.html"
    ;;
  2)
    PANEL_NAME="Pasarguard"
    REPO_RAW="$BASE_URL/pasarguard.html"
    INSTALL_DIR="/var/lib/pasarguard/templates/subscription"
    OUTPUT_FILE="$INSTALL_DIR/index.html"
    ;;
  3)
    PANEL_NAME="Marzban"
    REPO_RAW="$BASE_URL/marzban.html"
    INSTALL_DIR="/var/lib/marzban/templates/subscription"
    OUTPUT_FILE="$INSTALL_DIR/index.html"
    ;;
esac

# ── Summary ─────────────────────────────────────────────────────
echo ""
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "  Panel  : ${GRN}${PANEL_NAME}${RST}"
echo -e "  Theme  : ${GRN}${THEME_NAME}${RST}"
echo -e "  Brand  : ${GRN}${BRAND_UPPER}${RST}"
echo -e "  Path   : ${GRN}${OUTPUT_FILE}${RST}"
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo ""
read -rp "  Confirm install? [Y/n]: " CONFIRM
CONFIRM="${CONFIRM:-Y}"
[[ ! "$CONFIRM" =~ ^[Yy]$ ]] && echo -e "${YLW}  Cancelled.${RST}" && exit 0

echo ""
TMP_FILE=$(mktemp /tmp/ghost_sub_XXXXXX.html)

# ── Download ────────────────────────────────────────────────────
echo -e "${BLD}[1/4]${RST} Downloading template..."
if ! curl -fsSL "$REPO_RAW" -o "$TMP_FILE"; then
  echo -e "${RED}[✗] Download failed. Check your connection.${RST}"
  rm -f "$TMP_FILE"; exit 1
fi
echo -e "    ${GRN}✓ Downloaded${RST}"

# ── Branding ────────────────────────────────────────────────────
echo -e "${BLD}[2/4]${RST} Applying your branding..."
sed -i "s|YOUR BRAND|${BRAND_UPPER}|g" "$TMP_FILE"
echo -e "    ${GRN}✓ Branding applied${RST}"

# ── Apply default theme ──────────────────────────────────────────
echo -e "${BLD}[3/4]${RST} Applying theme..."
case "$THEME_CHOICE" in
  1) sed -i "s/^let themeIndex = [0-9];/let themeIndex = 0;/" "$TMP_FILE" ;;
  2) sed -i "s/^let themeIndex = [0-9];/let themeIndex = 1;/" "$TMP_FILE" ;;
  3) sed -i "s/^let themeIndex = [0-9];/let themeIndex = 2;/" "$TMP_FILE" ;;
esac
echo -e "    ${GRN}✓ Theme: ${THEME_NAME}${RST}"

# ── Install ──────────────────────────────────────────────────────
echo -e "${BLD}[4/4]${RST} Installing..."
mkdir -p "$INSTALL_DIR"
cp "$TMP_FILE" "$OUTPUT_FILE"
chmod 644 "$OUTPUT_FILE"
rm -f "$TMP_FILE"

# PWA manifest
MANIFEST_SRC="$(dirname "$0")/manifest.json"
MANIFEST_DST="$(dirname "$OUTPUT_FILE")/manifest.json"
if [[ -f "$MANIFEST_SRC" ]]; then
  cp "$MANIFEST_SRC" "$MANIFEST_DST"
  chmod 644 "$MANIFEST_DST"
  echo -e "    ${GRN}✓ manifest.json installed${RST}"
else
  # اگه manifest.json کنار اسکریپت نبود، یه نسخه inline می‌سازیم
  cat > "$MANIFEST_DST" << 'MEOF'
{"name":"Ghost Sub","short_name":"Sub","display":"standalone","background_color":"#05070a","theme_color":"#ff2a2a","start_url":"./","icons":[{"src":"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'><rect width='192' height='192' rx='32' fill='%23ff2a2a'/><text y='130' x='96' text-anchor='middle' font-size='110' font-family='sans-serif'>👻</text></svg>","sizes":"192x192","type":"image/svg+xml"}]}
MEOF
  chmod 644 "$MANIFEST_DST"
  echo -e "    ${GRN}✓ manifest.json created${RST}"
fi

echo -e "    ${GRN}✓ Installed${RST}"

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

