from pathlib import Path
import sqlite3
from datetime import datetime

# Shared SQLite Database

DB_FILE = str(
    Path(__file__).resolve().parent / "orders.db"
)


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_db():

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        # Orders Table

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (

            id TEXT PRIMARY KEY,

            customer TEXT NOT NULL,

            product TEXT NOT NULL,

            qty INTEGER NOT NULL,

            status TEXT NOT NULL,

            worker TEXT,

            tracking_number TEXT,

            created_at TEXT NOT NULL
        )
        """)

        # Timeline / Audit Log

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS timeline (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id TEXT NOT NULL,

            timestamp TEXT NOT NULL,

            stage TEXT NOT NULL,

            worker TEXT
        )
        """)

        # Users Table

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL
        )
        """)

        # Inventory Table

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            product TEXT UNIQUE NOT NULL,

            stock INTEGER NOT NULL,

            reorder_level INTEGER DEFAULT 5,

            price REAL,

            updated_at TEXT NOT NULL

        )
        """)

        # seed initial inventory
        # ensure price column exists for older DBs
        try:
            cursor.execute("ALTER TABLE inventory ADD COLUMN price REAL")
        except Exception:
            pass
        # ensure image_path column exists
        try:
            cursor.execute("ALTER TABLE inventory ADD COLUMN image_path TEXT")
        except Exception:
            pass

        try:
            seed_inventory()
        except Exception:
            pass

        conn.commit()


# ==========================================
# CREATE ORDER
# ==========================================

def add_order(
    order_id,
    customer,
    product,
    qty
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO orders
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
                (
                order_id,
                customer,
                product,
                qty,
                "Pending in Queue",
                "Unassigned",
                "Pending",
                timestamp
            )
        )

        cursor.execute(
            """
            INSERT INTO timeline
            (
                order_id,
                timestamp,
                stage,
                worker
            )
            VALUES
            (
                ?, ?, ?, ?
            )
            """,
                (
                order_id,
                timestamp,
                "Order Created",
                None
            )
        )

        conn.commit()


# ==========================================
# UPDATE STATUS
# ==========================================

def update_order_status(
    order_id,
    status,
    worker=None,
    tracking=None
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        if worker:

            cursor.execute(
                """
                UPDATE orders
                SET
                    status=?,
                    worker=?
                WHERE id=?
                """,
                (
                    status,
                    worker,
                    order_id
                )
            )

        elif tracking:

            cursor.execute(
                """
                UPDATE orders
                SET
                    status=?,
                    tracking_number=?
                WHERE id=?
                """,
                (
                    status,
                    tracking,
                    order_id
                )
            )

        else:

            cursor.execute(
                """
                UPDATE orders
                SET
                    status=?
                WHERE id=?
                """,
                (
                    status,
                    order_id
                )
            )

        cursor.execute(
            """
            INSERT INTO timeline
            (
                order_id,
                timestamp,
                stage,
                worker
            )
            VALUES
            (
                ?, ?, ?, ?
            )
            """,
            (
                order_id,
                timestamp,
                status,
                worker
            )
        )

        conn.commit()


# ==========================================
# GET ALL ORDERS
# ==========================================

def get_all_orders():

    with sqlite3.connect(DB_FILE) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM orders
        ORDER BY created_at DESC
        """)

        return cursor.fetchall()


# ==========================================
# GET CUSTOMER ORDERS
# ==========================================

def get_customer_orders(
    customer_name
):

    with sqlite3.connect(DB_FILE) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM orders
            WHERE customer=?
            ORDER BY created_at DESC
            """,
            (customer_name,)
        )

        return cursor.fetchall()


# ==========================================
# GET TIMELINE
# ==========================================

def get_timeline(
    order_id
):

    with sqlite3.connect(DB_FILE) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM timeline
            WHERE order_id=?
            ORDER BY id
            """,
            (order_id,)
        )

        return cursor.fetchall()


# ==========================================
# CLEAR DATABASE (orders + timeline)
# ==========================================

def clear_database():

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute("DELETE FROM timeline")
        cursor.execute("DELETE FROM orders")

        conn.commit()


# ==========================================
# USERS
# ==========================================

def add_user(name, email, password, role):

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                password,
                role
            )
        )

        conn.commit()

def get_user(email):

    with sqlite3.connect(DB_FILE) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=?
            """,
            (email,)
        )

        return cursor.fetchone()


# ==========================================
# INVENTORY
# ==========================================

def seed_inventory():

    products = [

        ("Laptop", 20),
        ("Smartphone", 30),
        ("Keyboard", 50),
        ("Mouse", 60),
        ("Monitor", 15),
        ("Headset", 25)

    ]

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        for product, stock in products:

            cursor.execute(
                """
                INSERT OR IGNORE INTO inventory
                (
                    product,
                    stock,
                    price,
                    updated_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    product,
                    stock,
                    None,
                    timestamp
                )
            )

        conn.commit()


def get_inventory():

    with sqlite3.connect(DB_FILE) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM inventory
            ORDER BY product
            """
        )

        return cursor.fetchall()


def get_stock(product):

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT stock
            FROM inventory
            WHERE product=?
            """,
            (product,)
        )

        row = cursor.fetchone()

        return row[0] if row else 0


def add_inventory_item(product, stock, reorder_level=5, price=None):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO inventory
            (
                product,
                stock,
                reorder_level,
                price,
                image_path,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                product,
                stock,
                reorder_level,
                price,
                None,
                timestamp
            )
        )

        conn.commit()


def get_inventory_by_id(item_id):

    with sqlite3.connect(DB_FILE) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM inventory
            WHERE id=?
            """,
            (item_id,)
        )

        return cursor.fetchone()


def update_inventory_item(item_id, stock=None, reorder_level=None, price=None, image_path=None):

    fields = []
    params = []

    if stock is not None:
        fields.append("stock=?")
        params.append(stock)

    if reorder_level is not None:
        fields.append("reorder_level=?")
        params.append(reorder_level)

    if price is not None:
        fields.append("price=?")
        params.append(price)

    if image_path is not None:
        fields.append("image_path=?")
        params.append(image_path)

    if not fields:
        return

    params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    params.append(item_id)

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            f"""
            UPDATE inventory
            SET {', '.join(fields)}, updated_at=?
            WHERE id=?
            """,
            tuple(params)
        )

        conn.commit()


def has_active_orders_for_product(product):

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE product=?
            AND status NOT LIKE '%Completed%'
            """,
            (product,)
        )

        row = cursor.fetchone()

        return (row[0] if row else 0) > 0


def delete_inventory_item(item_id):

    item = get_inventory_by_id(item_id)

    if not item:
        return False, "Item not found"

    if has_active_orders_for_product(item['product']):
        return False, "Cannot delete: active orders exist for this product"

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM inventory
            WHERE id=?
            """,
            (item_id,)
        )

        conn.commit()

    return True, None


def deduct_stock(product, qty):

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE inventory
            SET stock = stock - ?,
                updated_at=?
            WHERE product=?
            """,
            (
                qty,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                product
            )
        )

        conn.commit()


def try_deduct_stock(product, qty):
    """Attempt to deduct stock only if enough is available. Returns True if deducted."""

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE inventory
            SET stock = stock - ?,
                updated_at=?
            WHERE product=? AND stock >= ?
            """,
            (
                qty,
                timestamp,
                product,
                qty
            )
        )

        conn.commit()

        return cursor.rowcount > 0


def update_stock(product, stock):

    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE inventory
            SET stock=?,
                updated_at=?
            WHERE product=?
            """,
            (
                stock,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                product
            )
        )

        conn.commit()


def get_order_summary_counts():
    """Return counts for total, completed, pending, out_of_stock."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status LIKE '%Completed%'")
        completed = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status LIKE '%Pending%' OR status LIKE '%Queue%'")
        pending = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Out of Stock'")
        out_of_stock = cursor.fetchone()[0]
    return {"total": total, "completed": completed, "pending": pending, "out_of_stock": out_of_stock}


def get_order_counts_by_product(limit=10):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT product, COUNT(*) as cnt
            FROM orders
            GROUP BY product
            ORDER BY cnt DESC
            LIMIT ?
            """,
            (limit,)
        )
        return cursor.fetchall()


def get_total_revenue():
    """Sum of qty * price where price exists in inventory."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT SUM(o.qty * IFNULL(i.price, 0))
            FROM orders o
            LEFT JOIN inventory i ON o.product = i.product
            """
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0.0


def reset_database():
    """Reset database to initial state: clear orders, timeline, and restore inventory."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    default_inventory = [
        ("Laptop", 20),
        ("Smartphone", 30),
        ("Keyboard", 50),
        ("Mouse", 60),
        ("Monitor", 15),
        ("Headset", 25)
    ]
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Delete all orders and timeline
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM timeline")
        
        # Reset inventory to default stock levels (preserve image paths and prices)
        for product, stock in default_inventory:
            cursor.execute(
                """
                UPDATE inventory
                SET stock=?, updated_at=?
                WHERE product=?
                """,
                (stock, timestamp, product)
            )
        
        conn.commit()

        