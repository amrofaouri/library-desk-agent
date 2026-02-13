import sqlite3
import os

DB_PATH = "db/library.db"


def seed():
    os.makedirs("db", exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed existing database.")

    conn = sqlite3.connect(DB_PATH)

    with open("db/schema.sql", "r") as f:
        conn.executescript(f.read())
    print("Schema created.")

    with open("db/seed.sql", "r") as f:
        conn.executescript(f.read())
    print("Seed data inserted.")

    cursor = conn.execute("SELECT COUNT(*) FROM books")
    print(f"Books: {cursor.fetchone()[0]}")

    cursor = conn.execute("SELECT COUNT(*) FROM customers")
    print(f"Customers: {cursor.fetchone()[0]}")

    cursor = conn.execute("SELECT COUNT(*) FROM orders")
    print(f"Orders: {cursor.fetchone()[0]}")

    cursor = conn.execute("SELECT COUNT(*) FROM order_items")
    print(f"Order items: {cursor.fetchone()[0]}")

    conn.close()
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed()