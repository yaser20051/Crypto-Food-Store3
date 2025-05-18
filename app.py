from flask import Flask, render_template, request, redirect, url_for
import uuid, threading, time

app = Flask(__name__)
orders = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create-order", methods=["POST"])
def create_order():
    amount = request.form["amount"]
    wallet = request.form["wallet"]
    order_id = str(uuid.uuid4())
    orders[order_id] = {"amount": amount, "wallet": wallet, "paid": False, "tx_id": None}

    # Start timeout watcher (5 minutes)
    threading.Thread(target=order_timeout_watcher, args=(order_id,), daemon=True).start()
    return redirect(url_for("track_order", order_id=order_id))

@app.route("/order/<order_id>")
def track_order(order_id):
    order = orders.get(order_id)
    if not order:
        return "الطلب غير موجود", 404
    return render_template("order.html", order_id=order_id, amount=order["amount"], wallet=order["wallet"],
                           paid=order["paid"], tx_id=order["tx_id"])

@app.route("/confirm-payment/<order_id>", methods=["POST"])
def confirm_payment(order_id):
    tx_id = request.form["tx_id"]
    if order_id in orders:
        orders[order_id]["paid"] = True
        orders[order_id]["tx_id"] = tx_id
        return redirect(url_for("payment_success"))
    return "طلب غير موجود", 404

@app.route("/success")
def payment_success():
    return render_template("success.html")

@app.route("/fail")
def payment_fail():
    return render_template("fail.html")

def order_timeout_watcher(order_id):
    time.sleep(300)  # 5 دقائق
    order = orders.get(order_id)
    if order and not order["paid"]:
        del orders[order_id]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
