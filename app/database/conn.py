import sqlite3

conn = sqlite3.connect("products.db")
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    price TEXT NOT NULL,
    availability INTEGER,
    img_url TEXT,
    date_checked TEXT DEFAULT (datetime('now', 'localtime'))
""")


c.execute("""
    CREATE TABLE IF NOT EXISTS price_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        price TEXT NOT NULL,
        availability INTEGER,
        date_checked TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
""")

conn.commit()
conn.close()
