<div align="center">

# 👻 Ghost Sub

### Premium Subscription Page Template

#### Compatible with 3X-UI · Pasarguard · Marzban

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![3X-UI](https://img.shields.io/badge/3X--UI-Compatible-brightgreen)](https://github.com/MHSanaei/3x-ui)
[![Pasarguard](https://img.shields.io/badge/Pasarguard-Compatible-blueviolet)](https://github.com/PasarGuard/panel)
[![Marzban](https://img.shields.io/badge/Marzban-Compatible-orange)](https://github.com/Gozargah/Marzban)
[![FA | EN](https://img.shields.io/badge/Language-FA%20%7C%20EN-blue)](.)

> یه کامند. پنلت. تمت. اسم برندت. کانالت. تموم.
>
> One command. Your panel. Your theme. Your brand. Done.

</div>

---

## 📸 Preview

| Red | Green | Blue/Purple |
|-----|-------|-------------|
| ![red](screenshots/preview-red.png) | ![green](screenshots/preview-green.png) | ![blue](screenshots/preview-blue.png) |

---

## ✨ امکانات

| امکان | توضیح |
|-------|-------|
| 🎨 **۳ تم رنگی** | قرمز · سبز · آبی-بنفش — انتخاب موقع نصب + تغییر توسط کاربر |
| 🌐 **دوزبانه** | فارسی (RTL) + انگلیسی، اتوماتیک تشخیص |
| 📊 **نمودار ترافیک** | حلقه انیمیشن‌دار مصرف |
| ⏳ **تایمر زنده** | ثانیه‌شمار تا انقضا |
| ⚠️ **هشدار خودکار** | بنر قرمز انقضا، بنر نارنجی حجم کم |
| 📋 **لیست کانفیگ** | فیلتر بر اساس پروتکل |
| 📲 **ایمپورت مستقیم** | Hiddify · Clash · SingBox · V2RayNG · Streisand · Shadowrocket |
| 📖 **راهنمای تعاملی** | مراحل اتصال برای هر اپ به فارسی/انگلیسی |
| 🔗 **QR Code** | بارکد اشتراک قابل اسکن |
| 🌌 **پس‌زمینه ذرات** | انیمیشن پارتیکل با خطوط اتصال |
| 📡 **دکمه تمدید** | لینک مستقیم به کانال تلگرام |
| 🕐 **آخرین اتصال** | نمایش زمان آخرین اتصال یوزر |

---

## ⚡ نصب — یه دستور

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/YASIN0ASADI/ghost-sub/main/install.sh)
```

اسکریپت **چهار سوال** ازت می‌پرسه:

1. 🖥️ پنل: **3X-UI** یا **Pasarguard** یا **Marzban**
2. 🎨 تم پیش‌فرض: **Red** یا **Green** یا **Blue/Purple**
3. 📛 اسم برند / سرویست
4. 📣 یوزرنیم کانال تلگرامت

> ✅ نیاز به ویرایش دستی نیست. همه چیز خودکاره.

---

## 🎨 تم‌ها

کاربر می‌تونه **توی صفحه** با زدن دکمه تم، بین سه رنگ جابجا بشه.
تم پیش‌فرض موقع نصب انتخاب میشه.

---

## 🎛️ فعال‌سازی

### 3X-UI
بعد از نصب → **پنل ادمین → Settings → Subscription → Sub Theme Directory**:
```
/etc/3x-ui/sub_templates/my-theme/
```

### Pasarguard
مطمئن شو این دو خط توی `/opt/pasarguard/.env` هست:
```
CUSTOM_TEMPLATES_DIRECTORY="/var/lib/pasarguard/templates/"
SUBSCRIPTION_PAGE_TEMPLATE="subscription/index.html"
```
بعد توی پنل: **Subscription Settings → Disable Subscription Template → OFF**
```bash
pasarguard restart
```

### Marzban
مطمئن شو این دو خط توی `/opt/marzban/.env` هست:
```
CUSTOM_TEMPLATES_DIRECTORY="/var/lib/marzban/templates/"
SUBSCRIPTION_PAGE_TEMPLATE="subscription/index.html"
```
```bash
systemctl restart marzban
```

---

## 🔧 چی جایگذاری میشه؟

| placeholder | جایگزین میشه با |
|-------------|----------------|
| `YOUR BRAND` | اسم برندت (بزرگ) |
| `@yourchannel` | یوزرنیم تلگرامت |
| `https://t.me/yourchannel` | لینک تلگرامت |

---

## 📁 ساختار فایل‌ها

```
ghost-sub/
├── sub.html          ← نسخه 3X-UI
├── pasarguard.html   ← نسخه Pasarguard
├── marzban.html      ← نسخه Marzban
├── install.sh        ← اسکریپت نصب
└── screenshots/      ← تصاویر پیش‌نمایش
```

---

## 🤝 کردیت و لایسنس

طراحی و ساخت توسط [@YASIN0ASADI](https://github.com/YASIN0ASADI)
##  TELEGRAM: https://t.me/Inv1n3ible

لایسنس [MIT](LICENSE) — استفاده، فورک و سفارشی‌سازی آزاده.
اگه مفید بود، یه ⭐ بزن ممنون میشم!

---

**‌‌                   ساخته شده با ❤️ برای جامعه VPN ایران.    **
