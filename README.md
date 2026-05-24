# 🤖 APK Cleaner Bot

Telegram guruhlarini zararli APK fayllardan himoya qiluvchi avtomatik moderatsiya boti.

---

## 📋 Loyiha tuzilmasi

```
apk_cleaner_bot/
│── bot.py              ← Asosiy fayl (ishga tushirish nuqtasi)
│── config.py           ← Konfiguratsiya (TOKEN, ADMIN_ID)
│── database.py         ← SQLite ma'lumotlar bazasi operatsiyalari
│── requirements.txt    ← Python kutubxonalari
│── README.md           ← Ushbu fayl
│── bot.log             ← Log fayli (avtomatik yaratiladi)
│
├── handlers/
│   │── __init__.py     ← Paket belgisi
│   │── start.py        ← /start buyrug'i handleri
│   │── admin.py        ← Admin panel handlerlari
│   │── group_events.py ← Guruh hodisalari handleri
│   └── apk_filter.py   ← APK aniqlash va moderatsiya
│
└── data/
    └── bot.db          ← SQLite bazasi (avtomatik yaratiladi)
```

---

## ⚙️ O'rnatish va ishga tushirish

### 1. Talablar

- Python 3.10 yoki undan yuqori
- pip paket menejeri
- Telegram bot tokeni

### 2. Loyihani yuklab olish

```bash
git clone https://github.com/yourusername/apk_cleaner_bot.git
cd apk_cleaner_bot
```

Yoki fayllarni to'g'ridan-to'g'ri nusxalash.

### 3. Virtual muhit yaratish (tavsiya etiladi)

```bash
python -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 4. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 5. Bot tokenini olish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot uchun nom va username bering
4. BotFather sizga token beradi (ko'rinishi: `123456789:ABC-DEF...`)
5. Bu tokenni `config.py` dagi `BOT_TOKEN` ga kiriting

### 6. Admin ID ni aniqlash

1. Telegram'da [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring
2. U sizning `Id` raqamingizni ko'rsatadi (masalan: `987654321`)
3. Bu raqamni `config.py` dagi `ADMIN_ID` ga kiriting

### 7. Konfiguratsiyani sozlash

`config.py` faylini oching va to'ldiring:

```python
BOT_TOKEN = "123456789:ABC-DEFghi..."  # BotFather tokeni
ADMIN_ID  = 987654321                   # Sizning Telegram ID ingiz
```

### 8. Botni ishga tushirish

```bash
python main.py
```

Konsolda quyidagi xabar ko'rinishi kerak:
```
2024-01-01 12:00:00 [INFO] __main__: Bot ishga tushdi: @YourBotName (ID: ...)
2024-01-01 12:00:00 [INFO] __main__: Polling boshlandi.
```

---

## 🔑 Bot uchun kerakli ruxsatlar

Botni guruhga qo'shgandan so'ng, uni **Administrator** qiling va quyidagi ruxsatlarni bering:

| Ruxsat | Nima uchun kerak |
|--------|-----------------|
| ✅ `can_delete_messages` | APK fayllarni o'chirish |
| ✅ `can_restrict_members` | APK yuborgan foydalanuvchini ban qilish |

> ⚠️ Bu ruxsatlarsiz bot APK fayllarni aniqlay oladi, lekin o'chira va ban qila olmaydi.

---

## 📱 Bot imkoniyatlari

### Guruhda:
- APK fayllarni avtomatik aniqlash (`.apk` kengaytma yoki MIME turi)
- Xabarni zudlik bilan o'chirish
- Yuboruvchini guruhdan ban qilish
- Guruhga ogohlantirish xabari yuborish (30 soniyadan keyin o'chadi)
- **Bonus:** Guruh adminlari ban qilinmaydi

### Admin paneli (private chat):
| Buyruq | Tavsif |
|--------|--------|
| `/admin` | Admin menyusini ko'rish |
| `/stats` | Statistika: guruhlar, qoidabuzarliklar, banlar |
| `/violations` | So'nggi 20 ta qoidabuzarlik |
| `/groups` | Barcha guruhlar ro'yxati |
| `/broadcast` | Barcha guruhlarga xabar yuborish |
| `/cancel` | Broadcast jarayonini bekor qilish |

### Foydalanuvchiga (private chat):
| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni ishga tushirish va ma'lumot olish |

---

## 🗄️ Ma'lumotlar bazasi

SQLite (`data/bot.db`) ikki jadvaldan iborat:

**`groups`** — Guruhlar:
- `group_id` — Guruh ID
- `group_title` — Guruh nomi
- `added_date` — Qo'shilgan sana

**`violations`** — Qoidabuzarliklar:
- `id` — Tartib raqami
- `user_id` — Foydalanuvchi ID
- `full_name` — To'liq ism
- `username` — Username (@handle)
- `group_id` — Guruh ID
- `group_title` — Guruh nomi
- `file_name` — APK fayl nomi
- `violation_date` — Sana va vaqt

---

## 📝 Eslatmalar

> **Telegram Bot API haqida:** Telegram Bot API rasmiy "report" (shikoyat) funksiyasini ta'minlamaydi. `reportChatMessage` kabi method mavjud emas. Bu faqat Telegram ilovasi orqali oddiy foydalanuvchilar amalga oshira oladigan amal. Shuning uchun bot faqat ban qilish bilan cheklanadi.

---

## 🐛 Muammolarni hal qilish

**Bot xabarlarni o'chirmayapti:**
→ Botga `can_delete_messages` ruxsatini bering

**Bot ban qilmayapti:**
→ Botga `can_restrict_members` ruxsatini bering

**`BOT_TOKEN not set` xatosi:**
→ `config.py` da `BOT_TOKEN` ni to'ldiring

**`ModuleNotFoundError`:**
→ `pip install -r requirements.txt` ni qayta ishga tushiring

---

## 📄 Litsenziya

MIT License — erkin foydalanishingiz mumkin.
