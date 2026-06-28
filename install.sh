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
BLD='\033[1m'
RST='\033[0m'

REPO_RAW_3XUI="https://raw.githubusercontent.com/YASIN0ASADI/ghost-sub/main/sub.html"
REPO_RAW_PG="https://raw.githubusercontent.com/YASIN0ASADI/ghost-sub/main/pasarguard.html"

clear
echo ""
echo -e "${CYN}╔══════════════════════════════════════════════════════════╗${RST}"
echo -e "${CYN}║${RST}         ${BLD}Ghost Sub — Universal Installer${RST}                 ${CYN}║${RST}"
echo -e "${CYN}║${RST}         github.com/YASIN0ASADI/ghost-sub               ${CYN}║${RST}"
echo -e "${CYN}╚══════════════════════════════════════════════════════════╝${RST}"
echo ""

# ── Root check ─────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}[✗] Run as root:  sudo bash install.sh${RST}"
  exit 1
fi

for cmd in curl sed; do
  command -v "$cmd" &>/dev/null || apt-get install -y "$cmd" -qq 2>/dev/null || true
done

# ── Panel selection ────────────────────────────────────────────
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "  ${BLD}Select your panel:${RST}"
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo ""
echo -e "  ${BLD}1)${RST} 3X-UI"
echo -e "  ${BLD}2)${RST} Pasarguard"
echo ""

while true; do
  read -rp "  ➤ Enter 1 or 2: " PANEL_CHOICE
  PANEL_CHOICE=$(echo "$PANEL_CHOICE" | xargs)
  if [[ "$PANEL_CHOICE" == "1" || "$PANEL_CHOICE" == "2" ]]; then
    break
  fi
  echo -e "  ${RED}[✗] Please enter 1 or 2.${RST}"
done

echo ""

# ── Branding info ──────────────────────────────────────────────
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

BRAND_UPPER=$(echo "$BRAND_NAME" | tr '[:lower:]' '[:upper:]')

# ── Set paths based on panel ───────────────────────────────────
if [[ "$PANEL_CHOICE" == "1" ]]; then
  PANEL_NAME="3X-UI"
  REPO_RAW="$REPO_RAW_3XUI"
  INSTALL_DIR="/etc/3x-ui/sub_templates/my-theme"
  OUTPUT_FILE="$INSTALL_DIR/index.html"
else
  PANEL_NAME="Pasarguard"
  REPO_RAW="$REPO_RAW_PG"
  INSTALL_DIR="/var/lib/pasarguard/templates/subscription"
  OUTPUT_FILE="$INSTALL_DIR/index.html"
fi

# ── Summary ────────────────────────────────────────────────────
echo ""
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "  Panel  : ${GRN}${PANEL_NAME}${RST}"
echo -e "  Brand  : ${GRN}${BRAND_UPPER}${RST}"
echo -e "  Channel: ${GRN}${TG_HANDLE}${RST}"
echo -e "  Path   : ${GRN}${OUTPUT_FILE}${RST}"
echo -e "${CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo ""
read -rp "  Confirm install? [Y/n]: " CONFIRM
CONFIRM="${CONFIRM:-Y}"
[[ ! "$CONFIRM" =~ ^[Yy]$ ]] && echo -e "${YLW}  Cancelled.${RST}" && exit 0

echo ""
TMP_FILE=$(mktemp /tmp/ghost_sub_XXXXXX.html)

# ── Download ───────────────────────────────────────────────────
echo -e "${BLD}[1/4]${RST} Downloading template..."
if ! curl -fsSL "$REPO_RAW" -o "$TMP_FILE"; then
  echo -e "${RED}[✗] Download failed. Check your connection.${RST}"
  rm -f "$TMP_FILE"; exit 1
fi
echo -e "    ${GRN}✓ Downloaded${RST}"

# ── Branding ───────────────────────────────────────────────────
echo -e "${BLD}[2/4]${RST} Applying your branding..."
sed -i "s|YOUR BRAND|${BRAND_UPPER}|g"          "$TMP_FILE"
sed -i "s|@yourchannel|${TG_HANDLE}|g"          "$TMP_FILE"
sed -i "s|https://t.me/yourchannel|${TG_URL}|g" "$TMP_FILE"
echo -e "    ${GRN}✓ Branding applied${RST}"

# ── Install ────────────────────────────────────────────────────
echo -e "${BLD}[3/4]${RST} Installing..."
mkdir -p "$INSTALL_DIR"
cp "$TMP_FILE" "$OUTPUT_FILE"
chmod 644 "$OUTPUT_FILE"
rm -f "$TMP_FILE"
echo -e "    ${GRN}✓ Installed${RST}"

# ── Restart panel ──────────────────────────────────────────────
echo -e "${BLD}[4/4]${RST} Reloading ${PANEL_NAME}..."
if [[ "$PANEL_CHOICE" == "1" ]]; then
  if systemctl is-active --quiet x-ui 2>/dev/null; then
    systemctl restart x-ui && echo -e "    ${GRN}✓ x-ui restarted${RST}" \
      || echo -e "    ${YLW}⚠  Restart manually: systemctl restart x-ui${RST}"
  else
    echo -e "    ${YLW}⚠  Run manually: systemctl restart x-ui${RST}"
  fi
else
  if command -v pasarguard &>/dev/null; then
    pasarguard restart && echo -e "    ${GRN}✓ Pasarguard restarted${RST}" \
      || echo -e "    ${YLW}⚠  Restart manually: pasarguard restart${RST}"
  else
    echo -e "    ${YLW}⚠  Run manually: pasarguard restart${RST}"
  fi
fi

# ── Done ───────────────────────────────────────────────────────
echo ""
echo -e "${GRN}╔══════════════════════════════════════════════════════════╗${RST}"
echo -e "${GRN}║   ✓  Done! Ghost Sub installed successfully.             ║${RST}"
echo -e "${GRN}╚══════════════════════════════════════════════════════════╝${RST}"
echo ""
echo -e "  ${BLD}Template path:${RST}"
echo -e "  ${CYN}${OUTPUT_FILE}${RST}"
echo ""

if [[ "$PANEL_CHOICE" == "1" ]]; then
  echo -e "  ${BLD}Activate in 3X-UI panel:${RST}"
  echo -e "  ${YLW}Panel Settings → Subscription → Subscription Template Path${RST}"
  echo -e "  Enter: ${YLW}/etc/3x-ui/sub_templates/my-theme/${RST}"
else
  echo -e "  ${BLD}Activate in Pasarguard:${RST}"
  echo -e "  Edit ${YLW}/opt/pasarguard/.env${RST} and make sure these lines exist:"
  echo -e "  ${YLW}CUSTOM_TEMPLATES_DIRECTORY=\"/var/lib/pasarguard/templates/\"${RST}"
  echo -e "  ${YLW}SUBSCRIPTION_PAGE_TEMPLATE=\"subscription/index.html\"${RST}"
  echo -e "  Then run: ${YLW}pasarguard restart${RST}"
fi

echo ""
echo -e "  Brand: ${GRN}${BRAND_UPPER}${RST}   Channel: ${GRN}${TG_HANDLE}${RST}"
echo ""
