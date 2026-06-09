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

            for stage in STAGES:

                time.sleep(
                    random.uniform(1, 3)
                )

                if stage == "Validating Payment":

                    database.update_order_status(
                        oid,
                        stage,
                        worker=name
                    )

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

        "WorkerGamma"
    ]:

        threading.Thread(
            target=worker_loop,
            args=(w,),
            daemon=True
        ).start()