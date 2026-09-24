#!/usr/bin/env python3
"""
Ghost Sub — Usage Tracker (Pasarguard)
──────────────────────────────────────
هر N دقیقه با API پنل Pasarguard لاگین می‌کنه، مصرف تمام یوزرها رو
می‌خونه و یه تاریخچه‌ی سبک (snapshot) کنار فایل تمپلیت ذخیره می‌کنه.

خروجی: usage_<username>.json کنار index.html
{
  "username": "...",
  "points": [ {"t": 1719999999000, "used": 123456789}, ... ]
}

تمپلیت (pasarguard.html) این فایل رو fetch می‌کنه و نمودار مصرف رو می‌کشه.
"""

import json
import os
import sys
import time
import logging
from datetime import datetime, timezone

try:
    import httpx
except ImportError:
    print("Missing dependency: pip install httpx --break-system-packages")
    sys.exit(1)

# ── Config (از فایل کنار اسکریپت خونده میشه) ────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracker_config.json")

MAX_POINTS_PER_USER = 500      # سقف نقاط ذخیره‌شده به ازای هر یوزر
RETENTION_DAYS = 60            # نقاط قدیمی‌تر از این حذف میشن

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ghost-tracker] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ghost-tracker")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        log.error(f"Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    required = ["panel_url", "admin_username", "admin_password", "output_dir"]
    for key in required:
        if key not in cfg or not cfg[key]:
            log.error(f"Missing required config key: {key}")
            sys.exit(1)
    cfg.setdefault("interval_minutes", 15)
    cfg.setdefault("verify_ssl", True)
    return cfg


def get_token(client: httpx.Client, base_url: str, username: str, password: str) -> str:
    """لاگین به API پنل و گرفتن Bearer token."""
    resp = client.post(
        f"{base_url.rstrip('/')}/api/admin/token",
        data={"username": username, "password": password},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_all_users(client: httpx.Client, base_url: str, token: str) -> list:
    """گرفتن لیست تمام کاربران با صفحه‌بندی."""
    users = []
    offset = 0
    limit = 200
    headers = {"Authorization": f"Bearer {token}"}

    while True:
        resp = client.get(
            f"{base_url.rstrip('/')}/api/users",
            headers=headers,
            params={"offset": offset, "limit": limit},
        )
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("users", [])
        users.extend(batch)

        total = data.get("total", len(users))
        offset += limit
        if offset >= total or not batch:
            break

    return users


def load_history(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            log.warning(f"Corrupt history file, starting fresh: {path}")
    return {"username": None, "points": []}


def save_history(path: str, history: dict):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False)
    os.replace(tmp_path, path)  # atomic write


def prune_points(points: list) -> list:
    """نگه‌داشتن فقط RETENTION_DAYS اخیر و سقف MAX_POINTS_PER_USER."""
    cutoff = int(time.time() * 1000) - RETENTION_DAYS * 24 * 3600 * 1000
    points = [p for p in points if p["t"] >= cutoff]
    if len(points) > MAX_POINTS_PER_USER:
        # نمونه‌برداری یکنواخت به‌جای برش خام، تا شکل نمودار حفظ بشه
        step = len(points) / MAX_POINTS_PER_USER
        points = [points[int(i * step)] for i in range(MAX_POINTS_PER_USER)]
    return points


def run_once(cfg: dict):
    base_url = cfg["panel_url"]
    output_dir = cfg["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    with httpx.Client(timeout=20.0, verify=cfg["verify_ssl"]) as client:
        try:
            token = get_token(client, base_url, cfg["admin_username"], cfg["admin_password"])
        except httpx.HTTPError as e:
            log.error(f"Login failed: {e}")
            return

        try:
            users = get_all_users(client, base_url, token)
        except httpx.HTTPError as e:
            log.error(f"Failed to fetch users: {e}")
            return

    now_ms = int(time.time() * 1000)
    updated = 0

    for user in users:
        username = user.get("username")
        used_traffic = user.get("used_traffic", 0)
        if not username:
            continue

        safe_name = "".join(c for c in username if c.isalnum() or c in ("-", "_", "."))
        out_path = os.path.join(output_dir, f"usage_{safe_name}.json")

        history = load_history(out_path)
        history["username"] = username
        points = history.get("points", [])

        # فقط اگه تغییری کرده یا فاصله زمانی کافی گذشته، نقطه جدید اضافه کن
        if not points or points[-1]["used"] != used_traffic:
            points.append({"t": now_ms, "used": used_traffic})
        elif now_ms - points[-1]["t"] > cfg["interval_minutes"] * 60 * 1000 * 4:
            # حتی اگه تغییر نکرده، هر چند دوره یه نقطه ثابت ثبت کن (خط صاف تو نمودار)
            points.append({"t": now_ms, "used": used_traffic})

        history["points"] = prune_points(points)
        save_history(out_path, history)
        updated += 1

    log.info(f"Updated {updated} user usage files in {output_dir}")


def main():
    cfg = load_config()
    interval = cfg["interval_minutes"] * 60

    log.info(f"Ghost Tracker started. Panel: {cfg['panel_url']}  Interval: {cfg['interval_minutes']}m")

    while True:
        try:
            run_once(cfg)
        except Exception as e:
            log.exception(f"Unexpected error: {e}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
