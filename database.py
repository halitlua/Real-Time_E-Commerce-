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

        