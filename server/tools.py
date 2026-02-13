import sqlite3
import json
from langchain_core.tools import tool
from typing import Optional

DB_PATH = "db/library.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@tool
def find_books(q: str, by: str = "title") -> str:
    """Search for books by title or author.
    
    Args:
        q: The search query string
        by: Search field - either "title" or "author"
    
    Returns:
        JSON string with list of matching books
    """
    conn = get_db()
    try:
        if by == "author":
            rows = conn.execute(
                "SELECT isbn, title, author, genre, price, stock FROM books WHERE author LIKE ? ORDER BY title",
                (f"%{q}%",)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT isbn, title, author, genre, price, stock FROM books WHERE title LIKE ? ORDER BY title",
                (f"%{q}%",)
            ).fetchall()
        
        results = [dict(row) for row in rows]
        if not results:
            return json.dumps({"message": f"No books found matching '{q}' by {by}.", "results": []})
        return json.dumps({"message": f"Found {len(results)} book(s).", "results": results})
    finally:
        conn.close()


@tool
def create_order(customer_id: int, items: list[dict]) -> str:
    """Create a new order for a customer and reduce stock accordingly.
    
    Args:
        customer_id: The ID of the customer placing the order
        items: List of items, each with 'isbn' (str) and 'qty' (int)
    
    Returns:
        JSON string with the new order ID and stock updates
    """
    conn = get_db()
    try:
        customer = conn.execute("SELECT id, name FROM customers WHERE id = ?", (customer_id,)).fetchone()
        if not customer:
            return json.dumps({"error": f"Customer with ID {customer_id} not found."})
        
        for item in items:
            book = conn.execute("SELECT isbn, title, stock FROM books WHERE isbn = ?", (item["isbn"],)).fetchone()
            if not book:
                return json.dumps({"error": f"Book with ISBN {item['isbn']} not found."})
            if book["stock"] < item["qty"]:
                return json.dumps({"error": f"Insufficient stock for '{book['title']}'. Available: {book['stock']}, Requested: {item['qty']}"})
        
        cursor = conn.execute(
            "INSERT INTO orders (customer_id) VALUES (?)",
            (customer_id,)
        )
        order_id = cursor.lastrowid
        
        stock_updates = []
        for item in items:
            book = conn.execute("SELECT price, title, stock FROM books WHERE isbn = ?", (item["isbn"],)).fetchone()
            conn.execute(
                "INSERT INTO order_items (order_id, isbn, qty, price_at_purchase) VALUES (?, ?, ?, ?)",
                (order_id, item["isbn"], item["qty"], book["price"])
            )
            new_stock = book["stock"] - item["qty"]
            conn.execute(
                "UPDATE books SET stock = ? WHERE isbn = ?",
                (new_stock, item["isbn"])
            )
            stock_updates.append({
                "isbn": item["isbn"],
                "title": book["title"],
                "qty_ordered": item["qty"],
                "new_stock": new_stock
            })
        
        conn.commit()
        return json.dumps({
            "message": f"Order {order_id} created successfully for customer '{customer['name']}'.",
            "order_id": order_id,
            "stock_updates": stock_updates
        })
    except Exception as e:
        conn.rollback()
        return json.dumps({"error": str(e)})
    finally:
        conn.close()


@tool
def restock_book(isbn: str, qty: int) -> str:
    """Restock a book by adding quantity to current stock.
    
    Args:
        isbn: The ISBN of the book to restock
        qty: The quantity to add to stock
    
    Returns:
        JSON string with updated stock information
    """
    conn = get_db()
    try:
        book = conn.execute("SELECT isbn, title, stock FROM books WHERE isbn = ?", (isbn,)).fetchone()
        if not book:
            return json.dumps({"error": f"Book with ISBN {isbn} not found."})
        
        new_stock = book["stock"] + qty
        conn.execute("UPDATE books SET stock = ? WHERE isbn = ?", (new_stock, isbn))
        conn.commit()
        
        return json.dumps({
            "message": f"Restocked '{book['title']}' by {qty}.",
            "isbn": isbn,
            "title": book["title"],
            "previous_stock": book["stock"],
            "added": qty,
            "new_stock": new_stock
        })
    finally:
        conn.close()


@tool
def update_price(isbn: str, price: float) -> str:
    """Update the price of a book.
    
    Args:
        isbn: The ISBN of the book
        price: The new price
    
    Returns:
        JSON string with updated price information
    """
    conn = get_db()
    try:
        book = conn.execute("SELECT isbn, title, price FROM books WHERE isbn = ?", (isbn,)).fetchone()
        if not book:
            return json.dumps({"error": f"Book with ISBN {isbn} not found."})
        
        old_price = book["price"]
        conn.execute("UPDATE books SET price = ? WHERE isbn = ?", (price, isbn))
        conn.commit()
        
        return json.dumps({
            "message": f"Price updated for '{book['title']}'.",
            "isbn": isbn,
            "title": book["title"],
            "old_price": old_price,
            "new_price": price
        })
    finally:
        conn.close()


@tool
def order_status(order_id: int) -> str:
    """Get the status and details of an order.
    
    Args:
        order_id: The ID of the order to look up
    
    Returns:
        JSON string with order details
    """
    conn = get_db()
    try:
        order = conn.execute(
            """SELECT o.id, o.customer_id, c.name as customer_name, o.order_date, o.status
               FROM orders o JOIN customers c ON o.customer_id = c.id
               WHERE o.id = ?""",
            (order_id,)
        ).fetchone()
        
        if not order:
            return json.dumps({"error": f"Order {order_id} not found."})
        
        items = conn.execute(
            """SELECT oi.isbn, b.title, oi.qty, oi.price_at_purchase
               FROM order_items oi JOIN books b ON oi.isbn = b.isbn
               WHERE oi.order_id = ?""",
            (order_id,)
        ).fetchall()
        
        total = sum(item["qty"] * item["price_at_purchase"] for item in items)
        
        return json.dumps({
            "order_id": order["id"],
            "customer": order["customer_name"],
            "date": order["order_date"],
            "status": order["status"],
            "items": [dict(item) for item in items],
            "total": round(total, 2)
        })
    finally:
        conn.close()


@tool
def inventory_summary() -> str:
    """Get inventory summary showing all books, highlighting low-stock titles (stock <= 5).
    
    Returns:
        JSON string with inventory summary
    """
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT isbn, title, author, price, stock FROM books ORDER BY stock ASC"
        ).fetchall()
        
        all_books = [dict(row) for row in rows]
        low_stock = [b for b in all_books if b["stock"] <= 5]
        
        return json.dumps({
            "total_titles": len(all_books),
            "total_units": sum(b["stock"] for b in all_books),
            "low_stock_titles": low_stock,
            "all_books": all_books
        })
    finally:
        conn.close()


ALL_TOOLS = [find_books, create_order, restock_book, update_price, order_status, inventory_summary]