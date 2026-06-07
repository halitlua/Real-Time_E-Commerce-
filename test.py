import time
import uuid

import database
import engine

database.init_db()

database.add_order(
    f"LP-{str(uuid.uuid4())[:8]}",
    "John Doe",
    "Gaming Mouse",
    1
)

database.add_order(
    f"LP-{str(uuid.uuid4())[:8]}",
    "Jane Doe",
    "Keyboard",
    1
)

database.add_order(
    f"LP-{str(uuid.uuid4())[:8]}",
    "Bob Smith",
    "Monitor",
    1
)

engine.start_engine()

while True:
    time.sleep(1)