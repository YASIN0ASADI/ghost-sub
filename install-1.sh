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

echo ""

while true; do
  echo -e "  ${BLD}Telegram Channel${RST}  ${YLW}(e.g: @mychannel  or  t.me/mychannel)${RST}"
  read -rp "  ➤ Channel: " TG_RAW
  TG_RAW=$(echo "$TG_RAW" | xargs)
  TG_RAW="${TG_RAW#https://t.me/}"
  TG_RAW="${TG_RAW#t.me/}"
  [[ "$TG_RAW" != @* ]] && TG_RAW="@$TG_RAW"
  TG_HANDLE="$TG_RAW"
  TG_SLUG="${TG_HANDLE#@}"
  TG_URL="https://t.me/$TG_SLUG"
  [[ -n "$TG_SLUG" ]] && break
  echo -e "  ${RED}[✗] Cannot be empty.${RST}"
done

echo ""

echo -e "  ${BLD}Renew / Purchase Link${RST}  ${YLW}(لینک تمدید یا خرید — e.g: t.me/mybot  or  mysite.com/buy)${RST}"
echo -e "  ${DIM}(اگه نمی‌خوای لینک جداگانه بذاری، Enter بزن تا همون چنل تلگرام استفاده بشه)${RST}"
read -rp "  ➤ Renew URL (leave empty = use channel): " RENEW_RAW
RENEW_RAW=$(echo "$RENEW_RAW" | xargs)
if [[ -z "$RENEW_RAW" ]]; then
  RENEW_URL="$TG_URL"
else
  [[ "$RENEW_RAW" != http* ]] && RENEW_RAW="https://$RENEW_RAW"
  RENEW_URL="$RENEW_RAW"
fi

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
echo -e "  Channel: ${GRN}${TG_HANDLE}${RST}"
echo -e "  Renew  : ${GRN}${RENEW_URL}${RST}"
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
sed -i "s|YOUR BRAND|${BRAND_UPPER}|g"                    "$TMP_FILE"
sed -i "s|@yourchannel|${TG_HANDLE}|g"                    "$TMP_FILE"
sed -i "s|https://t.me/yourchannel|${TG_URL}|g"           "$TMP_FILE"
sed -i "s|https://renewurl.placeholder|${RENEW_URL}|g"    "$TMP_FILE"
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
echo -e "  Brand: ${GRN}${BRAND_UPPER}${RST}   Channel: ${GRN}${TG_HANDLE}${RST}   Theme: ${GRN}${THEME_NAME}${RST}"
echo -e "  Renew: ${GRN}${RENEW_URL}${RST}"
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
