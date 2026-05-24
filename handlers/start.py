# ============================================================
# handlers/start.py — /start buyrug'i handleri
# Faqat shaxsiy chat (private) uchun mo'ljallangan
# ============================================================

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
logger = logging.getLogger(__name__)

# Router yaratish — bu faylning barcha handlerlari shu routerga biriktiriladi
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    /start buyrug'ini qayta ishlash (faqat private chatda).
    Foydalanuvchiga botning vazifalari haqida ma'lumot beradi.
    """
    current_bot = message.bot

    # Bot username-ini aniqlash
    bot_user = await current_bot.get_me()
    bot_username = bot_user.username

    # Guruhga qo'shish tugmasini yaratish
    # ?startgroup=true — foydalanuvchiga botni guruhlaridan biriga qo'shish oynasini ochadi
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Guruhga qo'shish",
                    url=f"https://t.me/{bot_username}?startgroup=true"
                )
            ]
        ]
    )
    user_name = message.from_user.full_name

    welcome_text = (
        f"👋 Salom, <b>{user_name}</b>!\n\n"
        "🤖 Men <b>APK Cleaner Bot</b>man — Telegram guruhlarini "
        "zararli APK fayllardan tozalovchi avtomatik moderatsiya boti.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ <b>Men nima qilaman?</b>\n\n"
        "🔍 Guruhda yuborilgan barcha xabarlarni kuzataman\n"
        "🚫 APK fayllarni (<code>.apk</code>) aniqlagan zahoti o'chiraman\n"
        "⛔️ APK yuborgan foydalanuvchini guruhdan ban qilaman\n"
        "⚠️ Guruhga ogohlantirish xabari yuboran\n"
        "📊 Barcha qoidabuzarliklarni bazada saqlayman\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📋 <b>Bot ishlashi uchun guruhda quyidagi ruxsatlar kerak:</b>\n\n"
        "✅ Xabarlarni o'chirish (<code>can_delete_messages</code>)\n"
        "✅ Foydalanuvchilarni cheklash (<code>can_restrict_members</code>)\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "➕ Botni guruhingizga qo'shing va administrator qiling!\n\n"
        "💡 <i>Telegram APK fayllarni yuborish orqali zararli dasturlar "
        "tarqatishiga yo'l qo'ymang!</i>"
    )

    await message.answer(welcome_text,reply_markup=keyboard, parse_mode="HTML")
    logger.info(f"Start buyrug'i: {message.from_user.id} ({message.from_user.full_name})")
