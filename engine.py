import queue
import threading
import sqlite3
import time
import random

import database

database.init_db()

order_queue = queue.Queue()

WORKER_STATUS = {
    "Worker Alpha": "Idle",
    "Worker Beta": "Idle",
    "Worker Gamma": "Idle"
}

# Per-worker metrics
WORKER_METRICS = {w: {"orders_processed": 0, "busy_time": 0.0} for w in WORKER_STATUS}

START_TIME = time.time()

STAGES = [
    "Validating Payment",
    "Checking Inventory",
    "Generating Shipping Label",
    "Packaging Asset",
    "Ready for Shipment",
    "Completed"
]


def worker_loop(name):

    while True:

        oid = order_queue.get()

        WORKER_STATUS[name] = (
            f"Processing {oid}"
        )

        try:
            t_start = time.time()

            for stage in STAGES:

                time.sleep(
                    random.uniform(3, 5)
                )

                if stage == "Validating Payment":

                    database.update_order_status(
                        oid,
                        stage,
                        worker=name
                    )

                elif stage == "Checking Inventory":

                    # mark stage
                    database.update_order_status(
                        oid,
                        stage,
                        worker=name
                    )

                    # fetch product and qty for this order
                    with sqlite3.connect(database.DB_FILE) as conn:

                        conn.row_factory = sqlite3.Row

                        cur = conn.cursor()

                        cur.execute(
                            """
                            SELECT product, qty
                            FROM orders
                            WHERE id=?
                            """,
                            (oid,)
                        )

                        row = cur.fetchone()

                    if not row:

                        # cannot find order; mark and stop
                        database.update_order_status(
                            oid,
                            "Out of Stock"
                        )
                        break

                    product = row["product"]
                    qty = int(row["qty"])

                    # attempt atomic deduction
                    ok = database.try_deduct_stock(product, qty)

                    if ok:

                        # recorded in timeline via update_order_status above already
                        pass

                    else:

                        # mark out of stock and stop processing this order
                        database.update_order_status(
                            oid,
                            "Out of Stock",
                            worker=name
                        )

                        break

                elif stage == "Generating Shipping Label":

                    database.update_order_status(
                        oid,
                        stage,
                        tracking=
                        f"TRK-{random.randint(100000,999999)}"
                    )

                else:

                    database.update_order_status(
                        oid,
                        stage
                    )
            # record end time and add to worker busy_time
            t_end = time.time()
            try:
                WORKER_METRICS[name]["busy_time"] += (t_end - t_start)
            except Exception:
                pass

            # increment processed count if the order reached Completed
            try:
                # read current order status to detect completion
                with sqlite3.connect(database.DB_FILE) as conn:
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    cur.execute("SELECT status FROM orders WHERE id=?", (oid,))
                    r = cur.fetchone()
                    if r and isinstance(r["status"] if "status" in r.keys() else r[0], str) and ("Completed" in (r["status"] if "status" in r.keys() else r[0])):
                        WORKER_METRICS[name]["orders_processed"] += 1
            except Exception:
                pass

        finally:

            WORKER_STATUS[name] = "Idle"

            order_queue.task_done()

def poller():

    while True:

        with sqlite3.connect(
            database.DB_FILE
        ) as conn:

            c = conn.cursor()

            c.execute(
                """
                SELECT id
                FROM orders
                WHERE status=
                'Pending in Queue'
                """
            )

            for (oid,) in c.fetchall():

                c.execute(
                    """
                    UPDATE orders
                    SET status='Queueing...'
                    WHERE id=?
                    """,
                    (oid,)
                )

                conn.commit()

                order_queue.put(oid)

        time.sleep(1)

def start_engine():

    threading.Thread(
        target=poller,
        daemon=True
    ).start()

    for w in [

    "Worker Alpha",

    "Worker Beta",

    "Worker Gamma"

]:

        threading.Thread(
            target=worker_loop,
            args=(w,),
            daemon=True
        ).start()


def get_worker_metrics():
    now = time.time()
    uptime = max(1.0, now - START_TIME)
    total_busy = sum(v["busy_time"] for v in WORKER_METRICS.values())
    out = {}
    for name, v in WORKER_METRICS.items():
        busy = v["busy_time"]
        util = (busy / uptime) * 100.0
        out[name] = {
            "orders_processed": v["orders_processed"],
            "busy_time_seconds": round(busy, 3),
            "utilization_percent": round(util, 2)
        }
    return {"uptime_seconds": round(uptime, 2), "workers": out, "total_busy_time": round(total_busy, 3)}


def benchmark_processing(count, worker_count=3, products=None):
    """Synthetic benchmark that simulates processing `count` orders using `worker_count` workers.
    If `products` is provided, tasks will sample from that list (inventory items).
    This is isolated and does not interact with the main order queue or DB.
    """
    tasks = list(range(count))

    def process_task(idx):
        # simulate stage processing; optionally reference a product
        prod = None
        if products:
            prod = random.choice(products)
        for stage in STAGES:
            time.sleep(random.uniform(0.05, 0.12))

    # sequential
    if worker_count <= 1:
        t0 = time.perf_counter()
        for t in tasks:
            process_task(t)
        return time.perf_counter() - t0

    # parallel
    q = queue.Queue()
    for t in tasks:
        q.put(t)

    def worker():
        while True:
            try:
                q.get_nowait()
            except Exception:
                break
            process_task(0)
            q.task_done()

    t0 = time.perf_counter()
    threads = []
    for i in range(worker_count):
        th = threading.Thread(target=worker)
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    return time.perf_counter() - t0


def reset_worker_metrics():
    """Reset worker metrics to initial state."""
    global WORKER_METRICS
    for worker in WORKER_METRICS:
        WORKER_METRICS[worker] = {"orders_processed": 0, "busy_time": 0.0}
