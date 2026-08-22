"""Process 7.0 Place Order and 9.0 View Order History
Data stores: D5 Cart, D6 Orders, D7 Order Items, D2 Products, D8 Payments, D1 Users

Level 2 (1.5 Place Order):
 1.5.1 Capture Delivery Details
 1.5.2 Confirm Cart Items
 1.5.3 Create Order
 1.5.4 Create Order Items
 1.5.5 Update Product Stock
 1.5.6 Display Order Confirmation
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort

from ..auth_utils import login_required
from ..db import query, execute, get_db
from .cart import cart_items, cart_total

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    user_id = session["user_id"]

    items = cart_items(user_id)

    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart.view"))

    user = query(
        "SELECT * FROM users WHERE user_id=%s",
        (user_id,),
        one=True
    )

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not full_name or not phone or not address:
            flash(
                "Delivery name, phone and address are required.",
                "error"
            )

            return render_template(
                "customer/checkout.html",
                items=items,
                total=cart_total(items),
                user=user
            )

        for i in items:

            if i["quantity"] > i["stock"]:

                flash(
                    f"Only {i['stock']} left of {i['name']}.",
                    "error"
                )

                return redirect(url_for("cart.view"))

        # Product total
        product_total = cart_total(items)

        # Delivery charge - Rs 300
        delivery_charge = 300

        # Final order total
        total = product_total + delivery_charge

        db = get_db()
        cur = db.cursor()

        try:

            # Create order
            cur.execute(
                "INSERT INTO orders "
                "(user_id, full_name, phone, address, total_amount, status) "
                "VALUES (%s,%s,%s,%s,%s,'Pending')",
                (
                    user_id,
                    full_name,
                    phone,
                    address,
                    total
                )
            )

            order_id = cur.lastrowid

            # Create order items
            for i in items:

                cur.execute(
                    "INSERT INTO order_items "
                    "(order_id, product_id, quantity, unit_price) "
                    "VALUES (%s,%s,%s,%s)",
                    (
                        order_id,
                        i["product_id"],
                        i["quantity"],
                        i["price"]
                    )
                )

                # Update product stock
                cur.execute(
                    "UPDATE products "
                    "SET stock = stock - %s "
                    "WHERE product_id=%s",
                    (
                        i["quantity"],
                        i["product_id"]
                    )
                )

            # Clear cart
            cur.execute(
                "DELETE FROM cart WHERE user_id=%s",
                (user_id,)
            )

            db.commit()

        except Exception:

            db.rollback()
            raise

        finally:

            cur.close()

        return redirect(
            url_for(
                "payments.select",
                order_id=order_id
            )
        )

    # GET checkout page
    return render_template(
        "customer/checkout.html",
        items=items,
        total=cart_total(items) + 300,
        user=user
    )


@bp.route("/confirmation/<int:order_id>")
@login_required
def confirmation(order_id):

    """1.5.6 Display Order Confirmation"""

    order = _own_order(order_id)

    items = query(
        "SELECT oi.*, p.name "
        "FROM order_items oi "
        "JOIN products p ON p.product_id = oi.product_id "
        "WHERE oi.order_id=%s",
        (order_id,)
    )

    payment = query(
        "SELECT * FROM payments WHERE order_id=%s",
        (order_id,),
        one=True
    )

    return render_template(
        "customer/order_confirmation.html",
        order=order,
        items=items,
        payment=payment
    )


@bp.route("/history")
@login_required
def history():

    """9.0 View Order History"""

    orders = query(
        "SELECT o.*, "
        "pay.method AS payment_method, "
        "pay.status AS payment_status "
        "FROM orders o "
        "LEFT JOIN payments pay "
        "ON pay.order_id = o.order_id "
        "WHERE o.user_id=%s "
        "ORDER BY o.created_at DESC",
        (session["user_id"],)
    )

    return render_template(
        "customer/order_history.html",
        orders=orders
    )


@bp.route("/<int:order_id>")
@login_required
def detail(order_id):

    order = _own_order(order_id)

    items = query(
        "SELECT oi.*, p.name "
        "FROM order_items oi "
        "JOIN products p "
        "ON p.product_id = oi.product_id "
        "WHERE oi.order_id=%s",
        (order_id,)
    )

    payment = query(
        "SELECT * FROM payments "
        "WHERE order_id=%s",
        (order_id,),
        one=True
    )

    return render_template(
        "customer/order_detail.html",
        order=order,
        items=items,
        payment=payment
    )


def _own_order(order_id):

    order = query(
        "SELECT * FROM orders "
        "WHERE order_id=%s AND user_id=%s",
        (
            order_id,
            session["user_id"]
        ),
        one=True
    )

    if not order:
        abort(404)

    return order