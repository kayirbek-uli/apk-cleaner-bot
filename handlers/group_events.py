# ============================================================
# handlers/group_events.py — TO'LIQ TUZATILGAN VARIANTI
# ============================================================

import logging
from aiogram import Router, F
from aiogram.types import ChatMemberUpdated, Message
from aiogram.enums import ChatType, ChatMemberStatus  # ChatMemberStatus qo'shildi

import database as db

logger = logging.getLogger(__name__)
router = Router()


# ChatMemberUpdatedFilter o'rniga Magic Filter (F) ishlatamiz.
# Bu bot guruhga yangi a'zo bo'lib qo'shilgan holatni aniq ushlaydi.
@router.my_chat_member(
    F.new_chat_member.status.in_({ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR})
)
async def bot_added_to_group(event: ChatMemberUpdated) -> None:
    """
    Bot guruhga qo'shilganda ishga tushadigan handler.
    """
    # Agar bot avval ham guruhda bo'lgan bo'lsa va shunchaki huquqlari o'zgargan bo'lsa,
    # qayta-qayta salomlashmasligi uchun eski statusini tekshiramiz
    if event.old_chat_member and event.old_chat_member.status in ({ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR}):
        return

    chat = event.chat

    # Faqat guruh va superguruhlar uchun ishlaydi
    if chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return

    # Guruh ma'lumotlarini bazaga saqlash
    db.upsert_group(chat.id, chat.title or "Nomsiz guruh")
    logger.info(f"Bot yangi guruhga qo'shildi: {chat.title} ({chat.id})")

    welcome_msg = (
        "👋 Salom! Men <b>APK Cleaner Bot</b>man.\n\n"
        "🛡️ Endi bu guruhni APK fayllardan himoya qilaman.\n\n"
        "⚠️ <b>Diqqat:</b> Ishlashim uchun menga administrator huquqlari kerak:\n"
        "• Xabarlarni o'chirish\n"
        "• Foydalanuvchilarni cheklash\n\n"
        "✅ Ruxsatlar to'g'ri sozlangan bo'lsa, ishim boshlanadi!"
    )

    try:
        await event.answer(welcome_msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Guruhga xabar yuborishda xato: {e}")


@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def track_group_messages(message: Message) -> None:
    """
    Guruhdan kelgan har bir xabarni kuzatish.
    """
    chat = message.chat
    if chat.id and chat.title:
        db.upsert_group(chat.id, chat.title)