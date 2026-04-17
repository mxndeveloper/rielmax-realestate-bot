import aiosqlite
from typing import Optional, List, Dict
from datetime import datetime
from contextlib import asynccontextmanager

DB_PATH = "riel_bot.db"


async def init_db():
    """Initialize database with all necessary tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        
        # Users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                role TEXT,
                language TEXT DEFAULT 'ru',
                is_premium INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # External listings table (from CIAN, Avito, etc.)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS external_listings (
                external_id TEXT,
                source TEXT,
                title TEXT,
                description TEXT,
                price INTEGER,
                address TEXT,
                district TEXT,
                rooms INTEGER,
                area_total REAL,
                floor INTEGER,
                floors_total INTEGER,
                url TEXT,
                photos TEXT,
                is_sponsored INTEGER DEFAULT 0,
                last_seen TIMESTAMP,
                PRIMARY KEY (external_id, source)
            )
        ''')
        # User‑created listings table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                description TEXT,
                price INTEGER,
                district TEXT,
                address TEXT,
                photos TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        # Price alerts table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                district TEXT,
                max_price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        # ✅ Create indexes AFTER tables exist
        await db.execute("CREATE INDEX IF NOT EXISTS idx_external_listings_title ON external_listings(title)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_external_listings_district ON external_listings(district)")
        await db.commit()
    print("✅ Database initialized successfully.")


@asynccontextmanager
async def get_db():
    """Context manager for database connections."""
    async with aiosqlite.connect(DB_PATH) as db:
        yield db


class UserDB:
    """User-related database operations."""

    @staticmethod
    async def set_role(user_id: int, role: str) -> None:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO users (user_id, role) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET role = excluded.role",
                (user_id, role)
            )
            await db.commit()

    @staticmethod
    async def get_role(user_id: int) -> Optional[str]:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT role FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    @staticmethod
    async def set_language(user_id: int, lang: str) -> None:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO users (user_id, language) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET language = excluded.language",
                (user_id, lang)
            )
            await db.commit()

    @staticmethod
    async def get_language(user_id: int) -> str:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else "ru"

    @staticmethod
    async def set_premium(user_id: int, is_premium: bool = True) -> None:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO users (user_id, is_premium) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET is_premium = excluded.is_premium",
                (user_id, 1 if is_premium else 0)
            )
            await db.commit()

    @staticmethod
    async def is_premium(user_id: int) -> bool:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT is_premium FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return bool(row[0]) if row else False


class ListingDB:
    """User‑created listing operations."""

    @staticmethod
    async def add_listing(
        user_id: int,
        title: str,
        description: str,
        price: int,
        district: str = None,
        address: str = None,
        photos: str = None
    ) -> int:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO listings 
                (user_id, title, description, price, district, address, photos, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, title, description, price, district, address, photos, datetime.now().isoformat())
            )
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def get_user_listings(user_id: int) -> List[Dict]:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT * FROM listings WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]

    @staticmethod
    async def get_all_listings() -> List[Dict]:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT * FROM listings ORDER BY created_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]


class AlertDB:
    """Price alert operations."""

    @staticmethod
    async def add_alert(user_id: int, district: str, max_price: int) -> int:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "INSERT INTO price_alerts (user_id, district, max_price, created_at) VALUES (?, ?, ?, ?)",
                (user_id, district, max_price, datetime.now().isoformat())
            )
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def get_user_alerts(user_id: int) -> List[Dict]:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT * FROM price_alerts WHERE user_id = ?", (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]


async def save_listings_to_db(listings: list):
    """Insert or update external listings (used by update pipeline)."""
    async with aiosqlite.connect(DB_PATH) as db:
        for lst in listings:
            photos_str = ",".join(lst.get("photos", [])) if isinstance(lst.get("photos"), list) else lst.get("photos", "")
            await db.execute("""
                INSERT OR REPLACE INTO external_listings (
                    external_id, source, title, description, price, address, district,
                    rooms, area_total, floor, floors_total, url, photos,
                    is_sponsored, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lst.get("external_id"),
                lst.get("source"),
                lst.get("title"),
                lst.get("description"),
                lst.get("price"),
                lst.get("address"),
                lst.get("district"),
                lst.get("rooms"),
                lst.get("area_total"),
                lst.get("floor"),
                lst.get("floors_total"),
                lst.get("url"),
                photos_str,
                1 if lst.get("is_sponsored") else 0,
                lst.get("last_seen")
            ))
        await db.commit()