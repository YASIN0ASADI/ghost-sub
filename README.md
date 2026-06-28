<div align="center">

<br/>

# 👻 Ghost Sub
### Premium Subscription Page Template
#### Compatible with 3X-UI & Pasarguard

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![3X-UI](https://img.shields.io/badge/3X--UI-Compatible-brightgreen)](https://github.com/MHSanaei/3x-ui)
[![Pasargaurd](https://img.shields.io/badge/Pasarguard-Compatible-blueviolet)](https://github.com/PasarGuard/panel)
[![FA | EN](https://img.shields.io/badge/Language-FA%20%7C%20EN-blue)](.)
[![Stars](https://img.shields.io/github/stars/YASIN0ASADI/ghost-sub?style=social)](.)

<br/>

> یه کامند. اسم برندت. کانالت. تموم.
>
> One command. Your brand. Your channel. Done.

<br/>

</div>

---

## 📸 Preview

<div align="center">
<img src="screenshots/preview-blue.png" width="48%"/>
<img src="screenshots/preview-red.png" width="48%"/>
<br/><br/>
<img src="screenshots/preview-green.png" width="48%"/>
</div>

---

## ✨ این چیه؟

یه **صفحه سابسکریپشن سفارشی** برای پنل‌های [3X-UI](https://github.com/MHSanaei/3x-ui) و [Pasarguard](https://github.com/PasarGuard/panel).

به جای صفحه ساده پیش‌فرض، کاربرات یه **UI شیشه‌ای تاریک** می‌بینن که کاملاً با اسم و کانال خودت برند شده — با یه دستور نصب.

---

## 🎨 امکانات

| امکان | توضیح |
|---|---|
| 🎨 **۳ تم رنگی** | قرمز · سبز · آبی-بنفش — کاربر می‌تونه عوض کنه |
| 🌐 **دوزبانه** | فارسی (RTL) + انگلیسی، اتوماتیک تشخیص داده میشه |
| 📊 **نمودار ترافیک** | حلقه انیمیشن‌دار مصرف |
| ⏳ **تایمر زنده** | ثانیه شمار تا انقضای اشتراک |
| 📋 **لیست کانفیگ** | فیلتر بر اساس پروتکل: VLESS · VMess · Trojan · SS |
| 📲 **ایمپورت مستقیم** | یه کلیک برای Hiddify · Clash · SingBox · V2RayNG · Streisand · Shadowrocket |
| 🔗 **کد QR** | بارکد اشتراک قابل اسکن |
| 🩺 **دکتر اتصال** | راهنمای هوشمند عیب‌یابی برای کاربرا |
| 🌌 **پس‌زمینه ذرات** | انیمیشن پارتیکل با خطوط اتصال |
| 📡 **دکمه پشتیبانی** | لینک مستقیم به کانال تلگرام شما |
| 🏷️ **برند کامل** | اسم + کانالت خودکار توسط اسکریپت جایگذاری میشه |

---

## ⚡ نصب — یه دستور

<div align="center">
<img src="screenshots/install-preview.png" width="600"/>
</div>

<br/>

با دسترسی **root** روی سرور:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/YASIN0ASADI/ghost-sub/main/install.sh)
```

اسکریپت **سه سوال** ازت می‌پرسه:

1. 🖥️ پنل: **3X-UI** یا **Pasargaurd**
2. 📛 اسم برند / سرویست
3. 📣 یوزرنیم کانال تلگرامت

بعد خودش همه چیز رو انجام میده.

> ✅ نیاز به ویرایش دستی نیست. همه چیز خودکاره.

---

## 🎛️ فعال‌سازی

### 3X-UI

بعد از نصب، برو داخل **پنل ادمین 3X-UI**:

```
تنظیمات پنل ← Subscription ← Subscription Template Path
```

این مسیر رو وارد کن:

```
/etc/3x-ui/sub_templates/my-theme/
```

---

### Pasarguard

مطمئن شو این دو خط توی `/opt/pasarguard/.env` هست:

```
CUSTOM_TEMPLATES_DIRECTORY="/var/lib/pasarguard/templates/"
SUBSCRIPTION_PAGE_TEMPLATE="subscription/index.html"
```

بعد:

```bash
pasarguard restart
```

---

## 🗂️ نصب دستی (روش جایگزین)

```bash
git clone https://github.com/YASIN0ASADI/ghost-sub.git
cd ghost-sub
chmod +x install.sh
sudo bash install.sh
```

---

## 🔧 چی جایگذاری میشه؟

| placeholder در تمپلت | جایگزین میشه با |
|---|---|
| `YOUR BRAND` | اسم برندت (بزرگ) |
| `@yourchannel` | یوزرنیم تلگرامت |
| `https://t.me/yourchannel` | لینک تلگرامت |



## ❓ سوالات متداول

**سوال: با همه نسخه‌های 3X-UI کار می‌کنه؟**  
جواب: بله، با همه نسخه‌های اخیر که از custom template پشتیبانی می‌کنن.

**سوال: با چه نسخه‌ای از Pasarguard کار می‌کنه؟**  
جواب: با نسخه v3 به بالا.

**سوال: روی چند سرور می‌تونم نصب کنم؟**  
جواب: بله. دستور رو روی هر سرور اجرا کن و اطلاعات برندت رو بده.

**سوال: می‌تونم رنگ‌ها رو بیشتر سفارشی کنم؟**  
جواب: بله. بعد از نصب، فایل `index.html` رو در مسیر نصب مستقیم ویرایش کن.

---

## 🤝 کردیت و لایسنس

طراحی و ساخت توسط [@YASIN0ASADI](https://github.com/YASIN0ASADI)

لایسنس [MIT](LICENSE) — استفاده، فورک و سفارشی‌سازی آزاده.  
اگه مفید بود، یه ⭐ بزن ممنون میشم!

---

<div align="center">

**ساخته شده با ❤️ برای جامعه VPN ایران**

</div>
