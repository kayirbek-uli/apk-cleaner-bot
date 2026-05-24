# ============================================================
# config.py — Botning asosiy konfiguratsiya fayli
# Bu yerda BOT_TOKEN va ADMIN_ID ni o'rnating
# ============================================================

# Telegram bot tokeni (@BotFather orqali olinadi)
BOT_TOKEN = "TOKEN_BOT"

# Adminning Telegram user ID raqami
# Uni bilish uchun @userinfobot ga /start yuboring
ADMIN_ID = ADMIN_ID  # O'zingizning ID raqamingizni kiriting

# Ma'lumotlar bazasi fayli joylashuvi
DB_PATH = "data/bot.db"

# Log fayli nomi
LOG_FILE = "bot.log"

# Ogohlantirish xabarini o'chirish vaqti (soniyalarda)
WARNING_DELETE_TIMEOUT = 30

# Broadcast xabarlar orasidagi kutish vaqti (flood limitdan saqlanish)
BROADCAST_DELAY = 0.1  # 100 millisekund
