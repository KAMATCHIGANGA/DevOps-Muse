import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Read the existing SQLite products
sqlite_conn = sqlite3.connect("instance/starcourtuser.db")
sqlite_conn.row_factory = sqlite3.Row
products = sqlite_conn.execute(
    "SELECT id, name, category, price, unit, image_url FROM product"
).fetchall()
sqlite_conn.close()

# Connect to PostgreSQL without exposing credentials in the URL
db_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(db_url)

with engine.begin() as conn:
    existing = conn.execute(
        text("SELECT COUNT(*) FROM product")
    ).scalar_one()

    if existing != 0:
        raise RuntimeError(
            f"PostgreSQL product table already contains {existing} rows. "
            "Stopping to avoid overwriting data."
        )

    conn.execute(
        text("""
            INSERT INTO product
                (id, name, category, price, unit, image_url)
            VALUES
                (:id, :name, :category, :price, :unit, :image_url)
        """),
        [dict(row) for row in products],
    )

    # Ensure future auto-generated IDs continue after the imported IDs.
    conn.execute(text("""
        SELECT setval(
            pg_get_serial_sequence('product', 'id'),
            COALESCE((SELECT MAX(id) FROM product), 1),
            EXISTS (SELECT 1 FROM product)
        )
    """))

print(f"Successfully copied {len(products)} products to PostgreSQL.")
