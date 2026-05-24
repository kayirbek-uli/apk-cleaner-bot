# ============================================================
# database.py — SQLite ma'lumotlar bazasi bilan ishlash moduli
# Barcha CRUD operatsiyalar shu yerda amalga oshiriladi
# ============================================================

import sqlite3
import logging
from datetime import datetime
from config import DB_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """Ma'lumotlar bazasiga ulanish va Row factory o'rnatish."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Natijalarni dict sifatida qaytarish
    return conn


def init_db() -> None:
    """
    Barcha kerakli jadvallarni yaratish.
    Bot ishga tushganda bir marta chaqiriladi.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Guruhlar jadvali ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            group_id    INTEGER PRIMARY KEY,
            group_title TEXT    NOT NULL,
            added_date  TEXT    NOT NULL
        )
    """)

    # --- Qoidabuzarliklar jadvali ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            full_name      TEXT    NOT NULL,
            username       TEXT,
            group_id       INTEGER NOT NULL,
            group_title    TEXT    NOT NULL,
            file_name      TEXT    NOT NULL,
            violation_date TEXT    NOT NULL
        )
    """)

    # --- Broadcast holatini saqlash jadvali ---
    # Admin /broadcast buyrug'ini yuborganda pending holati saqlanadi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_state (
            admin_id    INTEGER PRIMARY KEY,
            is_waiting  INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")


# ============================================================
# GURUHLAR bilan ishlash funksiyalari
# ============================================================

def upsert_group(group_id: int, group_title: str) -> None:
    """
    Guruhni bazaga qo'shish yoki mavjud bo'lsa yangilash.
    INSERT OR REPLACE ishlatiladi.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO groups (group_id, group_title, added_date)
            VALUES (?, ?, ?)
            ON CONFLICT(group_id) DO UPDATE SET
                group_title = excluded.group_title
        """, (group_id, group_title, datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        logger.error(f"Guruhni saqlashda xato: {e}")
    finally:
        conn.close()


def get_all_groups() -> list[dict]:
    """Barcha guruhlarni ro'yxat sifatida qaytarish."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM groups ORDER BY added_date DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Guruhlarni olishda xato: {e}")
        return []
    finally:
        conn.close()


def get_groups_count() -> int:
    """Jami guruhlar sonini qaytarish."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM groups")
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Guruhlar sonini olishda xato: {e}")
        return 0
    finally:
        conn.close()


# ============================================================
# QOIDABUZARLIKLAR bilan ishlash funksiyalari
# ============================================================

def add_violation(
    user_id: int,
    full_name: str,
    username: str | None,
    group_id: int,
    group_title: str,
    file_name: str,
) -> None:
    """Yangi qoidabuzarlikni bazaga yozish."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO violations
                (user_id, full_name, username, group_id, group_title, file_name, violation_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            full_name,
            username or "",
            group_id,
            group_title,
            file_name,
            datetime.now().isoformat(),
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Qoidabuzarlikni saqlashda xato: {e}")
    finally:
        conn.close()


def get_latest_violations(limit: int = 20) -> list[dict]:
    """Eng so'nggi N ta qoidabuzarlikni qaytarish."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM violations
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Qoidabuzarliklarni olishda xato: {e}")
        return []
    finally:
        conn.close()


def get_violations_count() -> int:
    """Jami qoidabuzarliklar sonini qaytarish."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM violations")
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Qoidabuzarliklar sonini olishda xato: {e}")
        return 0
    finally:
        conn.close()


def get_banned_users_count() -> int:
    """Noyob ban qilingan foydalanuvchilar sonini qaytarish."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM violations")
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Ban qilinganlar sonini olishda xato: {e}")
        return 0
    finally:
        conn.close()


# ============================================================
# BROADCAST HOLATI bilan ishlash funksiyalari
# ============================================================

def set_broadcast_waiting(admin_id: int, is_waiting: bool) -> None:
    """Admin broadcast xabar kutayotganligini belgilash."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO broadcast_state (admin_id, is_waiting)
            VALUES (?, ?)
            ON CONFLICT(admin_id) DO UPDATE SET is_waiting = excluded.is_waiting
        """, (admin_id, 1 if is_waiting else 0))
        conn.commit()
    except Exception as e:
        logger.error(f"Broadcast holatini saqlashda xato: {e}")
    finally:
        conn.close()


def is_broadcast_waiting(admin_id: int) -> bool:
    """Admin broadcast xabar kutayotganmi yoki yo'qligini tekshirish."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT is_waiting FROM broadcast_state WHERE admin_id = ?",
            (admin_id,)
        )
        row = cursor.fetchone()
        return bool(row and row[0])
    except Exception as e:
        logger.error(f"Broadcast holatini olishda xato: {e}")
        return False
    finally:
        conn.close()
