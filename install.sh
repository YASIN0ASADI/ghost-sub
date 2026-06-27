#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║        3X-UI Subscription Template — Custom Installer       ║
# ║        github.com/YASIN0ASADI/ghost-sub                     ║
# ╚══════════════════════════════════════════════════════════════╝

set -e

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
CYN='\033[0;36m'
BLD='\033[1m'
RST='\033[0m'

REPO_RAW="https://raw.githubusercontent.com/YASIN0ASADI/ghost-sub/main/sub.html"
INSTALL_DIR="/etc/3x-ui/sub_templates/my-theme"
OUTPUT_FILE="$INSTALL_DIR/index.html"

clear
echo ""
echo -e "${CYN}╔══════════════════════════════════════════════════════════╗${RST}"
echo -e "${CYN}║${RST}       ${BLD}Ghost Sub — 3X-UI Template Installer${RST}              ${CYN}║${RST}"
echo -e "${CYN}║${RST}       github.com/YASIN0ASADI/ghost-sub                  ${CYN}║${RST}"
echo -e "${CYN}╚══════════════════════════════════════════════════════════╝${RST}"
echo ""

if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}[✗] Run as root:  sudo bash install.sh${RST}"
  exit 1
fi

for cmd in curl sed; do
  command -v "$cmd" &>/dev/null || apt-get install -y "$cmd" -qq 2>/dev/null || true
done

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
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "  Brand  : ${GRN}${BRAND_NAME}${RST}"
echo -e "  Channel: ${GRN}${TG_HANDLE}${RST}"
echo -e "  Path   : ${GRN}${OUTPUT_FILE}${RST}"
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo ""
read -rp "  Confirm install? [Y/n]: " CONFIRM
CONFIRM="${CONFIRM:-Y}"
[[ ! "$CONFIRM" =~ ^[Yy]$ ]] && echo -e "${YLW}  Cancelled.${RST}" && exit 0

echo ""
BRAND_UPPER=$(echo "$BRAND_NAME" | tr '[:lower:]' '[:upper:]')
TMP_FILE=$(mktemp /tmp/ghost_sub_XXXXXX.html)

echo -e "${BLD}[1/4]${RST} Downloading template..."
if ! curl -fsSL "$REPO_RAW" -o "$TMP_FILE"; then
  echo -e "${RED}[✗] Download failed. Check your connection.${RST}"
  rm -f "$TMP_FILE"; exit 1
fi
echo -e "    ${GRN}✓ Downloaded${RST}"

echo -e "${BLD}[2/4]${RST} Applying your branding..."
sed -i "s|YOUR BRAND|${BRAND_UPPER}|g"                   "$TMP_FILE"
sed -i "s|@yourchannel|${TG_HANDLE}|g"                   "$TMP_FILE"
sed -i "s|https://t.me/yourchannel|${TG_URL}|g"          "$TMP_FILE"
echo -e "    ${GRN}✓ Branding applied${RST}"

echo -e "${BLD}[3/4]${RST} Installing..."
mkdir -p "$INSTALL_DIR"
cp "$TMP_FILE" "$OUTPUT_FILE"
chmod 644 "$OUTPUT_FILE"
rm -f "$TMP_FILE"
echo -e "    ${GRN}✓ Installed${RST}"

echo -e "${BLD}[4/4]${RST} Reloading 3x-ui..."
if systemctl is-active --quiet x-ui 2>/dev/null; then
  systemctl restart x-ui && echo -e "    ${GRN}✓ x-ui restarted${RST}" \
    || echo -e "    ${YLW}⚠  Restart manually: systemctl restart x-ui${RST}"
else
  echo -e "    ${YLW}⚠  Run manually: systemctl restart x-ui${RST}"
fi

echo ""
echo -e "${GRN}╔══════════════════════════════════════════════════════════╗${RST}"
echo -e "${GRN}║   ✓  Done! Ghost Sub installed successfully.             ║${RST}"
echo -e "${GRN}╚══════════════════════════════════════════════════════════╝${RST}"
echo ""
echo -e "  ${BLD}Template path:${RST}"
echo -e "  ${CYN}${OUTPUT_FILE}${RST}"
echo ""
echo -e "  ${BLD}Activate in 3X-UI panel:${RST}"
echo -e "  ${YLW}Panel Settings → Subscription → Subscription Template Path${RST}"
echo -e "  Enter: ${YLW}/etc/3x-ui/sub_templates/my-theme/${RST}"
echo ""
echo -e "  Brand: ${GRN}${BRAND_UPPER}${RST}   Channel: ${GRN}${TG_HANDLE}${RST}"
echo ""
