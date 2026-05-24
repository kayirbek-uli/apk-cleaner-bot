# ============================================================
# handlers/apk_filter.py — APK fayllarni aniqlash va o'chirish
# ============================================================

import asyncio
import logging
from datetime import datetime

from aiogram import Router, Bot, F  # F qo'shildi
from aiogram.enums import ChatType
from aiogram.types import Message

import database as db
from config import WARNING_DELETE_TIMEOUT

logger = logging.getLogger(__name__)

router = Router()

# APK MIME turi konstantasi
APK_MIME_TYPE = "application/vnd.android.package-archive"
APK_EXTENSION = ".apk"


def is_apk_file(message: Message) -> bool:
    """Xabarda APK fayl borligini tekshirish."""
    doc = message.document
    if not doc:
        return False

    if doc.file_name and doc.file_name.lower().endswith(APK_EXTENSION):
        return True

    if doc.mime_type and doc.mime_type.lower() == APK_MIME_TYPE:
        return True

    return False


async def check_bot_permissions(bot: Bot, chat_id: int) -> tuple[bool, bool]:
    """Botning guruhda kerakli ruxsatlari borligini tekshirish."""
    try:
        bot_member = await bot.get_chat_member(chat_id, bot.id)
        # Aiogram 3.x da ruxsatlar 'can_delete_messages' kabi atributlarda bo'ladi
        can_delete = getattr(bot_member, "can_delete_messages", False)
        can_restrict = getattr(bot_member, "can_restrict_members", False)
        return can_delete, can_restrict
    except Exception as e:
        logger.error(f"Ruxsatlarni tekshirishda xato: {e}")
        return False, False


async def is_user_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Foydalanuvchi guruh admini yoki yaratuvchisi ekanligini tekshirish."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        logger.error(f"Admin statusini tekshirishda xato: {e}")
        return False


async def delete_warning_after_timeout(
        bot: Bot,
        chat_id: int,
        message_id: int,
        timeout: int
) -> None:
    """Ogohlantirish xabarini belgilangan vaqtdan keyin o'chirish."""
    await asyncio.sleep(timeout)
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass  # Xabar allaqachon o'chirilgan bo'lishi mumkin


# TUZATILGAN FILTR:
@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def handle_apk_message(message: Message, bot: Bot) -> None:
    """Guruhda kelgan xabarni APK uchun tekshirish va zarur choralar ko'rish."""

    # 1. APK faylmi tekshiruvi (faqat document bo'lsa davom etadi)
    if not message.document or not is_apk_file(message):
        return

    chat = message.chat
    user = message.from_user

    if not user:
        return

    file_name = message.document.file_name or "unknown.apk"

    # 2. Botning ruxsatlarini tekshirish
    can_delete, can_restrict = await check_bot_permissions(bot, chat.id)

    if not can_delete or not can_restrict:
        missing = []
        if not can_delete: missing.append("❌ Xabarlarni o'chirish")
        if not can_restrict: missing.append("❌ Foydalanuvchilarni cheklash")

        perm_msg = (
                "⚠️ <b>APK topildi, lekin ruxsatlarim yetarli emas!</b>\n\n"
                "Menga quyidagilarni bering:\n" + "\n".join(missing)
        )
        try:
            await message.answer(perm_msg, parse_mode="HTML")
        except:
            pass
        return

    # 3. Adminlarni tekshirish
    if await is_user_admin(bot, chat.id, user.id):
        return

    # 4. APK xabarini o'chirish
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"O'chirishda xato: {e}")

    # 5. Ban qilish
    banned_successfully = False
    try:
        await bot.ban_chat_member(chat.id, user.id)
        banned_successfully = True
    except Exception as e:
        logger.error(f"Ban qilishda xato: {e}")

    # 6. Ogohlantirish yuborish
    action_text = "ban qilindi ✅" if banned_successfully else "ban qilib bo'lmadi ❌"
    user_mention = f'<a href="tg://user?id={user.id}">{user.full_name}</a>'

    warning_text = (
        f"⚠️ <b>{user_mention}</b> APK fayl yubordi va guruhdan {action_text}.\n\n"
        f"📁 Fayl: <code>{file_name}</code>\n"
        f"<i>Bu xabar {WARNING_DELETE_TIMEOUT} soniyadan keyin o'chadi.</i>"
    )

    try:
        warning_msg = await bot.send_message(chat.id, warning_text, parse_mode="HTML")
        asyncio.create_task(
            delete_warning_after_timeout(
                bot, chat.id, warning_msg.message_id, WARNING_DELETE_TIMEOUT
            )
        )
    except Exception as e:
        logger.error(f"Xabar yuborishda xato: {e}")

    # 7. Bazaga yozish
    db.upsert_group(chat.id, chat.title or "Nomsiz guruh")
    db.add_violation(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
        group_id=chat.id,
        group_title=chat.title or "Nomsiz guruh",
        file_name=file_name,
    )