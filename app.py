from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request

import database
import engine
import uuid
import random

PRODUCTS = [

    "Laptop",
    "Smartphone",
    "Keyboard",
    "Mouse",
    "Monitor",
    "Headset"

]

CUSTOMERS = [

    "John Doe",
    "Jane Smith",
    "Alice Brown",
    "Bob Johnson",
    "Emma Davis",
    "Michael Lee"

]

app = Flask(__name__)

database.init_db()
engine.start_engine()


@app.route("/")
def admin():
    return render_template("admin.html")


@app.route("/customer")
def customer():
    return render_template("customer.html")


@app.route("/api/orders")
def api_orders():

    orders = []

    for row in database.get_all_orders():

        orders.append({
            "id": row["id"],
            "customer": row["customer"],
            "product": row["product"],
            "qty": row["qty"],
            "status": row["status"],
            "worker": row["worker"],
            "tracking": row["tracking_number"],
            "created": row["created_at"]
        })

    return jsonify(orders)


@app.route("/api/workers")
def api_workers():

    return jsonify(
        engine.WORKER_STATUS
    )


@app.route("/api/timeline/<order_id>")
def api_timeline(order_id):

    events = []

    for row in database.get_timeline(order_id):

        events.append({
            "timestamp": row["timestamp"],
            "stage": row["stage"],
            "worker": row["worker"]
        })

    return jsonify(events)


@app.route("/api/customer/orders/<customer>")
def customer_orders(customer):

    orders = []

    for row in database.get_customer_orders(customer):

        orders.append({

            "id": row["id"],
            "customer": row["customer"],
            "product": row["product"],
            "qty": row["qty"],
            "status": row["status"],
            "tracking": row["tracking_number"]

        })

    return jsonify(orders)


@app.route("/api/place-order", methods=["POST"])
def place_order():

    data = request.json

    order_id = (
        "LP-" +
        str(uuid.uuid4())[:8]
    )

    database.add_order(

        order_id,

        data["customer"],

        data["product"],

        int(data["qty"])

    )

    return jsonify({

        "success": True,

        "order_id": order_id

    })



@app.route("/api/generate/<int:count>")
def api_generate(count):

    import uuid
    import random

    customers = [
        "Alice", "Bob", "Carol", "Dave", "Eve",
        "Frank", "Grace", "Heidi"
    ]

    products = [
        "Widget A", "Widget B", "Gadget X", "Gadget Y",
        "Thingamajig"
    ]

    created = 0

    for i in range(count):
        oid = str(uuid.uuid4())[:8]
        customer = random.choice(customers)
        product = random.choice(products)
        qty = random.randint(1, 5)
        try:
            database.add_order(oid, customer, product, qty)
            created += 1
        except Exception:
            pass

    return jsonify({"created": created})


@app.route("/api/generate/10")
def api_generate_10():
    return api_generate(10)


@app.route("/api/generate/50")
def api_generate_50():
    return api_generate(50)


@app.route("/api/generate/100")
def api_generate_100():
    return api_generate(100)


@app.route("/api/clear", methods=["POST"])
def api_clear():
    try:
        database.clear_database()
        return jsonify({"cleared": True})
    except Exception:
        return jsonify({"cleared": False}), 500

@app.route("/api/place-order", methods=["POST"])
@app.route("/api/customer/orders/<customer>")
@app.route("/api/timeline/<order_id>")


@app.route("/api/generate/<int:count>", methods=["POST"])
def generate_orders(count):

    for _ in range(count):

        database.add_order(

            f"LP-{str(uuid.uuid4())[:8]}",

            random.choice(CUSTOMERS),

            random.choice(PRODUCTS),

            random.randint(1, 5)

        )

    return jsonify({

        "success": True,

        "count": count

    })

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )