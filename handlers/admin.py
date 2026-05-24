# ============================================================
# handlers/admin.py — Admin panel handlerlari
# Faqat ADMIN_ID ega bo'lgan foydalanuvchi uchun
# ============================================================

import asyncio
import logging
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.enums import ChatType

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

import database as db
from config import ADMIN_ID, BROADCAST_DELAY

logger = logging.getLogger(__name__)

router = Router()


def is_admin(message: Message) -> bool:
    """Xabar yuboruvchi admin ekanligini tekshirish."""
    return message.from_user and message.from_user.id == ADMIN_ID


# ============================================================
# ADMIN MENYUSI
# ============================================================

@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    """
    /admin — Admin panelini ko'rsatish.
    Faqat private chatda va faqat admin uchun.
    """
    if not is_admin(message):
        await message.answer("⛔️ Siz admin emassiz.")
        return

    # Statistikani olish
    groups_count = db.get_groups_count()
    violations_count = db.get_violations_count()
    banned_count = db.get_banned_users_count()

    admin_text = (
        "🛠 <b>Admin Panel — APK Cleaner Bot</b>\n\n"
        f"📊 <b>Umumiy statistika:</b>\n"
        f"  • Guruhlar: <b>{groups_count}</b>\n"
        f"  • Qoidabuzarliklar: <b>{violations_count}</b>\n"
        f"  • Ban qilinganlar: <b>{banned_count}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📋 <b>Buyruqlar:</b>\n\n"
        "/stats — Batafsil statistika\n"
        "/violations — So'nggi 20 ta qoidabuzarlik\n"
        "/groups — Barcha guruhlar ro'yxati\n"
        "/broadcast — Barcha guruhlarga xabar yuborish\n"
    )

    await message.answer(admin_text, parse_mode="HTML")
    logger.info(f"Admin panel ochildi: {message.from_user.id}")


# ============================================================
# STATISTIKA
# ============================================================

@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """/stats — Batafsil statistikani ko'rsatish."""
    if not is_admin(message):
        await message.answer("⛔️ Siz admin emassiz.")
        return

    groups_count = db.get_groups_count()
    violations_count = db.get_violations_count()
    banned_count = db.get_banned_users_count()

    stats_text = (
        "📊 <b>Batafsil statistika</b>\n\n"
        f"🏘 <b>Guruhlar:</b> {groups_count} ta\n"
        f"⚠️ <b>Qoidabuzarliklar:</b> {violations_count} ta\n"
        f"🚫 <b>Ban qilinganlar:</b> {banned_count} ta noyob foydalanuvchi\n\n"
        "<i>Ma'lumotlar real vaqtda yangilanadi.</i>"
    )

    await message.answer(stats_text, parse_mode="HTML")


# ============================================================
# QOIDABUZARLIKLAR RO'YXATI
# ============================================================

@router.message(Command("violations"))
async def cmd_violations(message: Message) -> None:
    """/violations — So'nggi 20 qoidabuzarlikni ko'rsatish."""
    if not is_admin(message):
        await message.answer("⛔️ Siz admin emassiz.")
        return

    violations = db.get_latest_violations(20)

    if not violations:
        await message.answer("✅ Hali hech qanday qoidabuzarlik yo'q.")
        return

    lines = ["⚠️ <b>So'nggi 20 ta qoidabuzarlik:</b>\n"]

    for i, v in enumerate(violations, 1):
        username_str = f"@{v['username']}" if v['username'] else "username yo'q"
        # ISO format sana → ko'rinishli formatga o'tkazish
        date_str = v['violation_date'][:19].replace("T", " ")

        lines.append(
            f"<b>{i}.</b> {v['full_name']} ({username_str})\n"
            f"   📁 <code>{v['file_name']}</code>\n"
            f"   🏘 {v['group_title']}\n"
            f"   🕐 {date_str}\n"
        )

    # Xabar juda uzun bo'lmasligi uchun bo'lib yuborish
    full_text = "\n".join(lines)

    # 4096 belgidan uzun bo'lsa bo'lib yuborish
    if len(full_text) <= 4096:
        await message.answer(full_text, parse_mode="HTML")
    else:
        # Xabarni 4096 ta belgi bo'laklarga bo'lish
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) > 4000:
                await message.answer(chunk, parse_mode="HTML")
                chunk = line
            else:
                chunk += "\n" + line
        if chunk:
            await message.answer(chunk, parse_mode="HTML")


# ============================================================
# GURUHLAR RO'YXATI
# ============================================================

@router.message(Command("groups"))
async def cmd_groups(message: Message) -> None:
    """/groups — Barcha guruhlar ro'yxatini ko'rsatish."""
    if not is_admin(message):
        await message.answer("⛔️ Siz admin emassiz.")
        return

    groups = db.get_all_groups()

    if not groups:
        await message.answer("📭 Hali hech qanday guruh yo'q.")
        return

    lines = [f"🏘 <b>Barcha guruhlar ({len(groups)} ta):</b>\n"]

    for i, g in enumerate(groups, 1):
        date_str = g['added_date'][:10]  # Faqat sana qismi
        lines.append(
            f"<b>{i}.</b> {g['group_title']}\n"
            f"   🆔 <code>{g['group_id']}</code>\n"
            f"   📅 Qo'shilgan: {date_str}\n"
        )

    full_text = "\n".join(lines)

    if len(full_text) <= 4096:
        await message.answer(full_text, parse_mode="HTML")
    else:
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) > 4000:
                await message.answer(chunk, parse_mode="HTML")
                chunk = line
            else:
                chunk += "\n" + line
        if chunk:
            await message.answer(chunk, parse_mode="HTML")


# ============================================================
# BROADCAST — Barcha guruhlarga xabar yuborish
# ============================================================

@router.message(Command("broadcast"))
async def cmd_broadcast_start(message: Message) -> None:
    """
    /broadcast — Broadcast jarayonini boshlash.
    Admin keyingi yuborganxabari barcha guruhlarga jo'natiladi.
    """
    if not is_admin(message):
        await message.answer("⛔️ Siz admin emassiz.")
        return

    groups_count = db.get_groups_count()

    if groups_count == 0:
        await message.answer("📭 Hali hech qanday guruh yo'q. Botni guruhga qo'shing.")
        return

    # Broadcast kutish holatini yoqish
    db.set_broadcast_waiting(ADMIN_ID, True)

    await message.answer(
        f"📢 <b>Broadcast rejimi faollashdi.</b>\n\n"
        f"Jami <b>{groups_count}</b> ta guruhga xabar yuboriladi.\n\n"
        f"✍️ Yubormoqchi bo'lgan xabaringizni yozing:\n"
        f"<i>(Bekor qilish uchun /cancel yuboring)</i>",
        parse_mode="HTML"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message) -> None:
    """/cancel — Broadcast rejimini bekor qilish."""
    if not is_admin(message):
        return

    if db.is_broadcast_waiting(ADMIN_ID):
        db.set_broadcast_waiting(ADMIN_ID, False)
        await message.answer("❌ Broadcast bekor qilindi.")
    else:
        await message.answer("ℹ️ Hech qanday faol jarayon yo'q.")


@router.message(F.chat.type == ChatType.PRIVATE, F.from_user.id == ADMIN_ID)
async def handle_broadcast_message(message: Message, bot: Bot) -> None:
    """
    Admin broadcast rejimida xabar yuborganida barcha guruhlarga jo'natish.
    
    Flood limitdan saqlanish uchun har bir xabar orasida BROADCAST_DELAY kutiladi.
    """
    # Broadcast kutayotgan bo'lsagina ishlaydi
    if not db.is_broadcast_waiting(ADMIN_ID):
        return

    # Broadcast holatini o'chirish
    db.set_broadcast_waiting(ADMIN_ID, False)

    groups = db.get_all_groups()

    if not groups:
        await message.answer("📭 Guruhlar topilmadi.")
        return

    await message.answer(
        f"⏳ <b>{len(groups)} ta guruhga xabar yuborilmoqda...</b>",
        parse_mode="HTML"
    )

    success_count = 0
    fail_count = 0
    fail_groups = []

    for group in groups:
        try:
            # Xabarni nusxalab yuborish (forward qilmasdan)
            await bot.copy_message(
                chat_id=group['group_id'],
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            success_count += 1
            logger.info(f"Broadcast yuborildi: {group['group_title']} ({group['group_id']})")

        except Exception as e:
            fail_count += 1
            fail_groups.append(group['group_title'])
            logger.error(
                f"Broadcast yuborishda xato: {group['group_title']} ({group['group_id']}): {e}"
            )

        # Flood limitdan saqlanish uchun kutish
        await asyncio.sleep(BROADCAST_DELAY)

    # Natijani adminga bildirish
    result_text = (
        f"📢 <b>Broadcast yakunlandi!</b>\n\n"
        f"✅ Muvaffaqiyatli: <b>{success_count}</b> ta guruh\n"
        f"❌ Muvaffaqiyatsiz: <b>{fail_count}</b> ta guruh\n"
    )

    if fail_groups:
        # Faqat birinchi 5 tasini ko'rsatish
        shown = fail_groups[:5]
        result_text += "\n<b>Muammoli guruhlar:</b>\n"
        result_text += "\n".join(f"• {g}" for g in shown)
        if len(fail_groups) > 5:
            result_text += f"\n<i>...va yana {len(fail_groups) - 5} ta</i>"

    await message.answer(result_text, parse_mode="HTML")
