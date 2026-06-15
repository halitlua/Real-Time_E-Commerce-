from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
from flask import url_for
from flask import session

import database
import engine
import uuid
import random
import os
from werkzeug.utils import secure_filename

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

app.secret_key = "PFS_SECRET_KEY"

database.init_db()
engine.start_engine()


@app.route("/")
def index():

    if session.get("role") == "ADMIN":

        return redirect("/admin")

    if session.get("role") == "CUSTOMER":

        return redirect("/customer")

    return redirect("/login")


@app.route("/admin")
def admin():

    if session.get("role") != "ADMIN":

        return redirect("/login")

    return render_template("admin.html")


@app.route("/customer")
def customer():

    if session.get("role") != "CUSTOMER":

        return redirect("/login")

    return render_template("customer.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        try:

            database.add_user(

                request.form["name"],

                request.form["email"],

                request.form["password"],

                "CUSTOMER"
            )

            return redirect("/login")

        except Exception:

            return "Email already exists."

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = database.get_user(

            request.form["email"]
        )

        if (

            user and

            user["password"] ==
            request.form["password"]

        ):

            session["user"] = user["name"]

            session["role"] = user["role"]

            if user["role"] == "ADMIN":

                return redirect("/admin")

            return redirect("/customer")

        return "Invalid credentials."

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():

    session.clear()

    return redirect("/login")


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


@app.route("/api/my-orders")
def my_orders():
    user = session.get('user')
    if not user:
        return jsonify([])

    orders = []
    for row in database.get_customer_orders(user):
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

    data = request.get_json(silent=True) or request.form

    product = data.get("product")

    qty = int(data.get("qty", 0))

    customer = session.get('user')
    if not customer:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    # Do not deduct stock at order placement; deduction is handled by workers.

    order_id = (
        "LP-" +
        str(uuid.uuid4())[:8]
    )

    database.add_order(
        order_id,
        customer,
        product,
        qty
    )

    return jsonify({

        "success": True,

        "order_id": order_id

    })



@app.route("/api/generate/<int:count>", methods=["GET", "POST"])
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


@app.route("/api/inventory")
def api_inventory():

    inv = []

    for row in database.get_inventory():

        # handle possible missing price column on older DBs
        try:
            price = row["price"]
        except Exception:
            price = None
        try:
            image = row["image_path"]
        except Exception:
            image = None

        inv.append({
            "id": row["id"],
            "product": row["product"],
            "stock": row["stock"],
            "reorder_level": row["reorder_level"],
            "price": price,
            "image_path": image,
            "updated_at": row["updated_at"]
        })

    return jsonify(inv)


@app.route('/api/products')
def api_products():
    """Return products for customer dropdown. By default return only items with stock > 0."""
    products = []
    for row in database.get_inventory():
        try:
            stock = int(row['stock'])
        except Exception:
            stock = 0

        # handle missing fields gracefully
        try:
            price = row['price']
        except Exception:
            price = None

        try:
            image = row['image_path']
        except Exception:
            image = None

        if stock > 0:
            products.append({
                'product': row['product'],
                'stock': stock,
                'price': price,
                'image_path': image
            })

    return jsonify(products)


@app.route('/api/worker-metrics')
def api_worker_metrics():
    try:
        stats = engine.get_worker_metrics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics')
def api_analytics():
    try:
        summary = database.get_order_summary_counts()
        most = database.get_order_counts_by_product()
        most_list = [{'product': r[0], 'count': r[1]} for r in most]
        revenue = database.get_total_revenue()
        return jsonify({
            'summary': summary,
            'most_ordered': most_list,
            'total_revenue': revenue
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/benchmark')
def api_benchmark():
    try:
        count = int(request.args.get('count', 10))
        # gather offered products from inventory (stock > 0)
        products = []
        for row in database.get_inventory():
            try:
                stock = int(row.get('stock', 0))
            except Exception:
                stock = 0
            if stock > 0:
                products.append(row.get('product'))

        # run sequential and parallel benchmarks (sequential uses 1 worker)
        seq = engine.benchmark_processing(count, worker_count=1, products=products)
        par = engine.benchmark_processing(count, worker_count=3, products=products)
        return jsonify({'count': count, 'sequential_seconds': seq, 'parallel_seconds': par})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/inventory')
def inventory_page():

    if session.get("role") != "ADMIN":
        return redirect('/login')

    return render_template('inventory.html')


@app.route('/api/inventory', methods=['POST'])
def api_add_inventory():

    if session.get('role') != 'ADMIN':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403

    # support multipart/form-data file upload or JSON
    try:
        body_json = request.get_json(silent=True)
        product = request.form.get('product') or (body_json and body_json.get('product'))
        stock = request.form.get('stock') or (body_json and body_json.get('stock'))
        reorder = request.form.get('reorder_level') or (body_json and body_json.get('reorder_level'))
        price = request.form.get('price') or (body_json and body_json.get('price'))

        stock = int(stock or 0)
        reorder = int(reorder or 5)
        price = float(price) if price not in (None, '') else None

        image = None
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename:
                fname = secure_filename(f.filename)
                target_dir = os.path.join(app.static_folder, 'products')
                os.makedirs(target_dir, exist_ok=True)
                save_path = os.path.join(target_dir, fname)
                f.save(save_path)
                image = os.path.join('products', fname)

        database.add_inventory_item(product, stock, reorder, price)

        # if image provided, update the last inserted item to include image_path
        if image:
            # fetch the item by product name
            with __import__('sqlite3').connect(database.DB_FILE) as conn:
                cur = conn.cursor()
                cur.execute("UPDATE inventory SET image_path=? WHERE product=?", (image, product))
                conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
def api_update_inventory(item_id):

    if session.get('role') != 'ADMIN':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403

    # support JSON or multipart formdata with optional image
    try:
        stock = None
        reorder = None
        price = None
        image = None

        body_json = request.get_json(silent=True)
        if body_json:
            stock = body_json.get('stock')
            reorder = body_json.get('reorder_level')
            price = body_json.get('price')
        else:
            stock = request.form.get('stock')
            reorder = request.form.get('reorder_level')
            price = request.form.get('price')

        stock = int(stock) if stock is not None and stock != '' else None
        reorder = int(reorder) if reorder is not None and reorder != '' else None
        price = float(price) if price not in (None, '') else None

        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename:
                fname = secure_filename(f.filename)
                target_dir = os.path.join(app.static_folder, 'products')
                os.makedirs(target_dir, exist_ok=True)
                save_path = os.path.join(target_dir, fname)
                f.save(save_path)
                image = os.path.join('products', fname)

        database.update_inventory_item(item_id, stock=stock, reorder_level=reorder, price=price, image_path=image)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
def api_delete_inventory(item_id):

    if session.get('role') != 'ADMIN':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403

    ok, msg = database.delete_inventory_item(item_id)

    if not ok:
        return jsonify({'success': False, 'message': msg}), 400

    return jsonify({'success': True})


@app.route('/api/admin/reset-database', methods=['POST'])
def api_reset_database():
    """Admin-only endpoint to reset the database to initial state."""
    
    if session.get('role') != 'ADMIN':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # Reset orders, timeline, and inventory
        database.reset_database()
        # Reset worker metrics
        engine.reset_worker_metrics()
        return jsonify({'success': True, 'message': 'Database reset successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


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



if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
