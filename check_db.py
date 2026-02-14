import sqlite3

conn = sqlite3.connect("db/library.db")

print("=== Messages ===")
rows = conn.execute("SELECT * FROM messages").fetchall()
for r in rows:
    print(r)

print("\n=== Tool Calls ===")
rows = conn.execute("SELECT * FROM tool_calls").fetchall()
for r in rows:
    print(r)

conn.close()