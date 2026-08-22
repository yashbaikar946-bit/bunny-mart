"""Process 6.0 Manage Cart (data store: D5 Cart, reads D2 Products)"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from ..auth_utils import login_required
from ..db import query, execute

bp = Blueprint("cart", __name__, url_prefix="/cart")


def cart_items(user_id):
    return query(
        "SELECT c.cart_id, c.quantity, p.product_id, p.name, p.price, p.image, p.stock "
        "FROM cart c JOIN products p ON p.product_id = c.product_id "
        "WHERE c.user_id=%s", (user_id,))


def cart_total(items):
    return sum(float(i["price"]) * i["quantity"] for i in items)


@bp.route("/")
@login_required
def view():
    items = cart_items(session["user_id"])
    return render_template("customer/cart.html", items=items, total=cart_total(items))


@bp.post("/add/<int:product_id>")
@login_required
def add(product_id):
    qty = max(1, request.form.get("quantity", type=int) or 1)
    product = query("SELECT stock FROM products WHERE product_id=%s", (product_id,), one=True)
    if not product or product["stock"] < 1:
        flash("Product is out of stock.", "error")
        return redirect(url_for("products.detail", product_id=product_id))
    execute(
        "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE quantity = LEAST(quantity + %s, %s)",
        (session["user_id"], product_id, min(qty, product["stock"]), qty, product["stock"]))
    flash("Added to cart.", "success")
    return redirect(url_for("cart.view"))


@bp.post("/update/<int:cart_id>")
@login_required
def update(cart_id):
    qty = request.form.get("quantity", type=int) or 1
    if qty < 1:
        execute("DELETE FROM cart WHERE cart_id=%s AND user_id=%s",
                (cart_id, session["user_id"]))
        flash("Item removed.", "success")
        return redirect(url_for("cart.view"))
    execute("UPDATE cart SET quantity=%s WHERE cart_id=%s AND user_id=%s",
            (qty, cart_id, session["user_id"]))
    flash("Cart updated.", "success")
    return redirect(url_for("cart.view"))


@bp.post("/remove/<int:cart_id>")
@login_required
def remove(cart_id):
    execute("DELETE FROM cart WHERE cart_id=%s AND user_id=%s",
            (cart_id, session["user_id"]))
    flash("Item removed.", "success")
    return redirect(url_for("cart.view"))
