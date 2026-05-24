# ============================================================
# main.py — APK Cleaner Bot asosiy fayli
# Botni ishga tushirish uchun: python main.py
# ============================================================

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Konfiguratsiya va ma'lumotlar bazasi
from config import BOT_TOKEN, LOG_FILE, DB_PATH
import database as db

# Handlerlar
from handlers import start, admin, group_events, apk_filter


# ============================================================
# LOGGING SOZLASH
# Konsolga va fayl (bot.log) ga bir vaqtda yozish
# ============================================================

def setup_logging() -> None:
    """Logging tizimini sozlash."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Root logger sozlash
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Konsolga chiqarish
            logging.StreamHandler(sys.stdout),
            # Faylga yozish
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ]
    )

    # aiogram kutubxonasining ortiqcha debug xabarlarini kamaytirish
    logging.getLogger("aiogram").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Logging tizimi ishga tushirildi.")


# ============================================================
# BOT ISHGA TUSHIRISH
# ============================================================

async def main() -> None:
    """
    Botni ishga tushirishning asosiy funksiyasi.
    
    1. Logging sozlanadi
    2. Ma'lumotlar bazasi yaratiladi
    3. Bot va Dispatcher yaratiladi
    4. Handlerlar ro'yxatdan o'tkaziladi
    5. Polling boshlanadi
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    # BOT_TOKEN tekshiruvi
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "BOT_TOKEN o'rnatilmagan! "
            "config.py faylidagi BOT_TOKEN ni to'ldiring."
        )
        sys.exit(1)

    # Ma'lumotlar bazasi papkasini yaratish (mavjud bo'lmasa)
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"Ma'lumotlar bazasi papkasi yaratildi: {db_dir}")

    # Ma'lumotlar bazasini ishga tushirish
    db.init_db()
    logger.info("Ma'lumotlar bazasi tayyor.")

    # Bot yaratish (HTML parse mode default sifatida)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Dispatcher yaratish
    dp = Dispatcher()

    # -------------------------------------------------------
    # HANDLERLARNI RO'YXATDAN O'TKAZISH
    # MUHIM: Tartibi ahamiyatli!
    # apk_filter birinchi bo'lishi kerak — u guruh xabarlarini ushlaydi
    # group_events ikkinchi — qolgan xabarlarni kuzatadi
    # -------------------------------------------------------
    dp.include_router(apk_filter.router)   # 1. APK aniqlash (yuqori prioritet)
    dp.include_router(start.router)         # 2. /start buyrug'i
    dp.include_router(admin.router)         # 3. Admin buyruqlari
    dp.include_router(group_events.router)  # 4. Guruh hodisalari (past prioritet)

    # Bot ma'lumotlarini olish va loglash
    try:
        bot_info = await bot.get_me()
        logger.info(
            f"Bot ishga tushdi: @{bot_info.username} "
            f"(ID: {bot_info.id}, Nom: {bot_info.full_name})"
        )
    except Exception as e:
        logger.error(f"Bot ma'lumotlarini olishda xato: {e}")
        sys.exit(1)

    logger.info("Polling boshlandi. Botni to'xtatish uchun Ctrl+C bosing.")

    # Botni ishga tushirish (polling rejimi)
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi (Ctrl+C).")
    except Exception as e:
        logger.critical(f"Kutilmagan xato: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Bot sessiyasi yopildi.")


if __name__ == "__main__":
    asyncio.run(main())
