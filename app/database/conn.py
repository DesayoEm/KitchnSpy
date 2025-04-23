import sqlite3
from typing import Optional, Dict, Any
from datetime import datetime
from app.infrastructure.log_service import logger


class Database:
    def __init__(self, db_path: str = "products.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                price TEXT NOT NULL,
                img_url TEXT,
                availability INTEGER,
                date_checked TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price TEXT NOT NULL,
                availability INTEGER,
                date_checked TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        self.conn.commit()

    def insert_or_update_product(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert new product or update existing by URL.
        Returns product ID.
        """
        try:
            self.cursor.execute("""
                INSERT INTO products (name, url, price, img_url, availability, date_checked)
                VALUES (:name, :url, :price, :img_url, :availability, :date_checked)
                ON CONFLICT(url) DO UPDATE SET
                    name = excluded.name,
                    price = excluded.price,
                    img_url = excluded.img_url,
                    availability = excluded.availability,
                    date_checked = excluded.date_checked
            """, data)

            self.conn.commit()
            logger.info(f"Inserted/Updated: {data['name']}")
            return self.cursor.lastrowid or self.get_product_id(data['url'])
        except Exception as e:

            logger.error(f"DB insert/update error for {data['name']}: {e}")
            return None

    def log_price(self, product_id: int, data: Dict[str, Any]):
        """Log price history for a product."""
        try:
            self.cursor.execute("""
                INSERT INTO price_log (product_id, price, availability, date_checked)
                VALUES (?, ?, ?, ?)
            """, (product_id, data["price"], data["availability"], data["date_checked"]))
            self.conn.commit()
            logger.info(f"Logged price for product_id={product_id}")
        except Exception as e:
            logger.error(f"Price log error for product_id={product_id}: {e}")

    def get_product_id(self, url: str) -> Optional[int]:
        self.cursor.execute("SELECT id FROM products WHERE url = ?", (url,))
        row = self.cursor.fetchone()
        return row["id"] if row else None

    def close(self):
        self.conn.close()
