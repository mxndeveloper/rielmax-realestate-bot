import aiosqlite
from typing import Optional, List, Dict
from datetime import datetime
from contextlib import asynccontextmanager

DB_PATH = "riel_bot.db"


async def init_db():
    """Initialize database with all necessary tables"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                role TEXT,
                language TEXT DEFAULT 'ru',
                is_premium BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Listings table (expanded for search and tracking)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                description TEXT,
                price INTEGER,
                district TEXT,
                address TEXT,
                photos TEXT,                    -- JSON string of file_ids
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

        await db.commit()
    print("✅ Database initialized successfully with users, listings, and price alerts")


@asynccontextmanager
async def get_db():
    """Context manager for database connections (used by menu.py etc.)"""
    async with aiosqlite.connect(DB_PATH) as db:
        yield db


class UserDB:
    """User-related database operations"""

    @staticmethod
    async def set_role(user_id: int, role: str) -> None:
        """Set user role without affecting other fields"""
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
            async with db.execute(
                "SELECT role FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    @staticmethod
    async def set_language(user_id: int, lang: str) -> None:
        """Set user language without affecting other fields"""
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
            async with db.execute(
                "SELECT language FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else "ru"

    @staticmethod
    async def set_premium(user_id: int, is_premium: bool = True) -> None:
        """Set premium status without affecting other fields"""
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
            async with db.execute(
                "SELECT is_premium FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return bool(row[0]) if row else False


class ListingDB:
    """Listing-related database operations"""

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
        """Add a new listing and return its ID"""
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
        """Get all listings for a user"""
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT * FROM listings WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]

    @staticmethod
    async def get_all_listings() -> List[Dict]:
        """Get all listings (useful for search)"""
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT * FROM listings ORDER BY created_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]


class AlertDB:
    """Price alert operations"""

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
            async with db.execute(
                "SELECT * FROM price_alerts WHERE user_id = ?", (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]