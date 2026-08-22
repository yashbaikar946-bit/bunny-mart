"""Admin Level 1 processes 1.0 - 8.0

 1.0 Admin Login            -> D10 Admin
 2.0 Manage Products        -> D2 Products (+ D3 Categories)
 3.0 Manage Categories      -> D3 Categories
 4.0 Manage Stock           -> D2 Products (+ D7 Order Items)
 5.0 Manage Customers       -> D1 Users
 6.0 Manage Orders          -> D6 Orders, D7 Order Items
 7.0 Manage Payments        -> D8 Payments (+ D6 Orders)
 8.0 Manage Contact Messages-> D9 Contact Messages
"""
import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, flash, abort, current_app
)

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from ..auth_utils import admin_required
from ..db import query, execute

bp = Blueprint("admin", __name__, url_prefix="/admin")

ORDER_STATUSES = [
    "Pending",
    "Confirmed",
    "Processing",
    "Shipped",
    "Delivered",
    "Cancelled"
]

PAYMENT_STATUSES = [
    "Pending",
    "Pending Verification",
    "Paid",
    "Failed"
]


# ---------------- 1.0 Admin Login ----------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = query(
            "SELECT * FROM admin WHERE username=%s",
            (username,),
            one=True
        )

        if admin and check_password_hash(
            admin["password_hash"],
            password
        ):
            session.clear()

            session["admin_id"] = admin["admin_id"]
            session["admin_username"] = admin["username"]

            return redirect(url_for("admin.dashboard"))

        flash("Invalid admin credentials.", "error")

    return render_template("admin/login.html")


# ---------------- Admin Forgot Password ----------------
@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Check empty fields
        if not username or not new_password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template("admin/forgot_password.html")

        # Password length
        if len(new_password) < 6:
            flash(
                "Password must be at least 6 characters.",
                "error"
            )
            return render_template("admin/forgot_password.html")

        # Confirm password
        if new_password != confirm_password:
            flash(
                "Passwords do not match.",
                "error"
            )
            return render_template("admin/forgot_password.html")

        # Check admin username
        admin = query(
            "SELECT admin_id FROM admin WHERE username=%s",
            (username,),
            one=True
        )

        if not admin:
            flash(
                "Admin username not found.",
                "error"
            )
            return render_template("admin/forgot_password.html")

        # Update password
        password_hash = generate_password_hash(new_password)

        execute(
            "UPDATE admin SET password_hash=%s WHERE admin_id=%s",
            (
                password_hash,
                admin["admin_id"]
            )
        )

        flash(
            "Password changed successfully. Please login.",
            "success"
        )

        return redirect(url_for("admin.login"))

    return render_template("admin/forgot_password.html")


# ---------------- Admin Logout ----------------
@bp.route("/logout")
def logout():

    session.pop("admin_id", None)
    session.pop("admin_username", None)

    return redirect(url_for("admin.login"))


# ---------------- Admin Dashboard ----------------
@bp.route("/")
@admin_required
def dashboard():

    stats = {
        "products": query(
            "SELECT COUNT(*) c FROM products",
            one=True
        )["c"],

        "customers": query(
            "SELECT COUNT(*) c FROM users",
            one=True
        )["c"],

        "orders": query(
            "SELECT COUNT(*) c FROM orders",
            one=True
        )["c"],

        "pending_payments": query(
            "SELECT COUNT(*) c FROM payments "
            "WHERE status IN ('Pending','Pending Verification')",
            one=True
        )["c"],

        "messages": query(
            "SELECT COUNT(*) c FROM contact_messages "
            "WHERE status='New'",
            one=True
        )["c"],
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats
    )


# ---------------- 2.0 Manage Products ----------------
def _save_image(file):

    if not file or not file.filename:
        return None

    ext = file.filename.rsplit(".", 1)[-1].lower()

    if ext not in {"png", "jpg", "jpeg", "webp"}:
        return None

    fname = (
        f"prod_{uuid.uuid4().hex[:8]}_"
        f"{secure_filename(file.filename)}"
    )

    file.save(
        os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            fname
        )
    )

    return fname


# ---------------- D11 Manage Payment QR ----------------

def _save_qr_image(file):

    if not file or not file.filename:
        return None

    ext = file.filename.rsplit(".", 1)[-1].lower()

    if ext not in {"png", "jpg", "jpeg", "webp"}:
        return None

    fname = (
        f"qr_{uuid.uuid4().hex[:8]}_"
        f"{secure_filename(file.filename)}"
    )

    file.save(
        os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            fname
        )
    )

    return fname


@bp.route("/payment_qr", methods=["GET", "POST"])
@admin_required
def payment_qr():

    if request.method == "POST":

        qr_file = request.files.get("qr_image")

        qr_image = _save_qr_image(qr_file)

        if not qr_image:

            flash(
                "Please upload a valid QR image.",
                "error"
            )

            return redirect(
                url_for("admin.payment_qr")
            )

        # Check existing QR
        existing = query(
            "SELECT qr_id, qr_image "
            "FROM payment_qr_settings "
            "ORDER BY qr_id ASC "
            "LIMIT 1",
            one=True
        )

        if existing:

            # Replace existing QR
            execute(
                "UPDATE payment_qr_settings "
                "SET qr_image=%s "
                "WHERE qr_id=%s",

                (
                    qr_image,
                    existing["qr_id"]
                )
            )

        else:

            # First QR upload
            execute(
                "INSERT INTO payment_qr_settings (qr_image) "
                "VALUES (%s)",

                (qr_image,)
            )

        flash(
            "Payment QR code updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.payment_qr")
        )

    # Get current QR
    qr = query(
        "SELECT * FROM payment_qr "
        "ORDER BY qr_id ASC "
        "LIMIT 1",
        one=True
    )

    return render_template(
        "admin/payment_qr.html",
        qr=qr
    )


@bp.route("/products")
@admin_required
def products():

    rows = query(
        "SELECT p.*, c.name AS category_name "
        "FROM products p "
        "LEFT JOIN categories c "
        "ON c.category_id=p.category_id "
        "ORDER BY p.product_id DESC"
    )

    return render_template(
        "admin/products.html",
        products=rows
    )


@bp.route("/products/add", methods=["GET", "POST"])
@admin_required
def product_add():

    categories = query(
        "SELECT * FROM categories ORDER BY name"
    )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        if not name:

            flash(
                "Product name is required.",
                "error"
            )

        else:

            execute(
                "INSERT INTO products "
                "(category_id, name, description, price, stock, image) "
                "VALUES (%s,%s,%s,%s,%s,%s)",

                (
                    request.form.get("category_id") or None,
                    name,
                    request.form.get(
                        "description",
                        ""
                    ).strip(),

                    request.form.get(
                        "price",
                        type=float
                    ) or 0,

                    request.form.get(
                        "stock",
                        type=int
                    ) or 0,

                    _save_image(
                        request.files.get("image")
                    )
                )
            )

            flash(
                "Product added.",
                "success"
            )

            return redirect(
                url_for("admin.products")
            )

    return render_template(
        "admin/product_form.html",
        product=None,
        categories=categories
    )


@bp.route(
    "/products/<int:product_id>/edit",
    methods=["GET", "POST"]
)
@admin_required
def product_edit(product_id):

    product = query(
        "SELECT * FROM products WHERE product_id=%s",
        (product_id,),
        one=True
    )

    if not product:
        abort(404)

    categories = query(
        "SELECT * FROM categories ORDER BY name"
    )

    if request.method == "POST":

        image = (
            _save_image(
                request.files.get("image")
            )
            or product["image"]
        )

        execute(
            "UPDATE products SET "
            "category_id=%s, name=%s, description=%s, "
            "price=%s, stock=%s, image=%s "
            "WHERE product_id=%s",

            (
                request.form.get(
                    "category_id"
                ) or None,

                request.form.get(
                    "name",
                    ""
                ).strip(),

                request.form.get(
                    "description",
                    ""
                ).strip(),

                request.form.get(
                    "price",
                    type=float
                ) or 0,

                request.form.get(
                    "stock",
                    type=int
                ) or 0,

                image,
                product_id
            )
        )

        flash(
            "Product updated.",
            "success"
        )

        return redirect(
            url_for("admin.products")
        )

    return render_template(
        "admin/product_form.html",
        product=product,
        categories=categories
    )


# ---------------- Product Delete Protection ----------------
@bp.post(
    "/products/<int:product_id>/delete"
)
@admin_required
def product_delete(product_id):

    # Check whether this product has already been
    # included in any customer order.
    order_item = query(
        "SELECT order_item_id "
        "FROM order_items "
        "WHERE product_id=%s "
        "LIMIT 1",
        (product_id,),
        one=True
    )

    # Product is already connected with customer order.
    if order_item:

        flash(
            "This product cannot be deleted because it has "
            "already been included in a customer order. "
            "To protect existing order history and customer "
            "records, this product cannot be removed.",
            "delete-warning"
        )

        return redirect(
            url_for("admin.products")
        )

    # Product has no customer order history.
    execute(
        "DELETE FROM products "
        "WHERE product_id=%s",
        (product_id,)
    )

    flash(
        "Product deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.products")
    )


# ---------------- 3.0 Manage Categories ----------------
@bp.route(
    "/categories",
    methods=["GET", "POST"]
)
@admin_required
def categories():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        if name:

            execute(
                "INSERT IGNORE INTO categories "
                "(name, description) VALUES (%s,%s)",

                (
                    name,
                    request.form.get(
                        "description",
                        ""
                    ).strip()
                )
            )

            flash(
                "Category added.",
                "success"
            )

        return redirect(
            url_for("admin.categories")
        )

    rows = query(
        "SELECT c.*, "
        "(SELECT COUNT(*) FROM products p "
        "WHERE p.category_id=c.category_id) "
        "AS product_count "
        "FROM categories c "
        "ORDER BY c.name"
    )

    return render_template(
        "admin/categories.html",
        categories=rows
    )


@bp.post(
    "/categories/<int:category_id>/edit"
)
@admin_required
def category_edit(category_id):

    execute(
        "UPDATE categories SET "
        "name=%s, description=%s "
        "WHERE category_id=%s",

        (
            request.form.get(
                "name",
                ""
            ).strip(),

            request.form.get(
                "description",
                ""
            ).strip(),

            category_id
        )
    )

    flash(
        "Category updated.",
        "success"
    )

    return redirect(
        url_for("admin.categories")
    )


@bp.post(
    "/categories/<int:category_id>/delete"
)
@admin_required
def category_delete(category_id):

    execute(
        "DELETE FROM categories "
        "WHERE category_id=%s",
        (category_id,)
    )

    flash(
        "Category deleted.",
        "success"
    )

    return redirect(
        url_for("admin.categories")
    )


# ---------------- 4.0 Manage Stock ----------------
@bp.route("/stock")
@admin_required
def stock():

    rows = query(
        "SELECT p.product_id, p.name, p.stock, "
        "COALESCE((SELECT SUM(oi.quantity) "
        "FROM order_items oi "
        "WHERE oi.product_id=p.product_id),0) "
        "AS sold "
        "FROM products p "
        "ORDER BY p.stock ASC"
    )

    return render_template(
        "admin/stock.html",
        products=rows
    )


@bp.post(
    "/stock/<int:product_id>/add"
)
@admin_required
def stock_add(product_id):

    qty = request.form.get(
        "quantity",
        type=int
    ) or 0

    execute(
        "UPDATE products SET stock = stock + %s "
        "WHERE product_id=%s",
        (qty, product_id)
    )

    flash(
        "Stock added.",
        "success"
    )

    return redirect(
        url_for("admin.stock")
    )


@bp.post(
    "/stock/<int:product_id>/set"
)
@admin_required
def stock_set(product_id):

    qty = max(
        0,
        request.form.get(
            "quantity",
            type=int
        ) or 0
    )

    execute(
        "UPDATE products SET stock=%s "
        "WHERE product_id=%s",
        (qty, product_id)
    )

    flash(
        "Stock updated.",
        "success"
    )

    return redirect(
        url_for("admin.stock")
    )


# ---------------- 5.0 Manage Customers ----------------
@bp.route("/customers")
@admin_required
def customers():

    rows = query(
        "SELECT user_id, name, email, phone, address, created_at, "
        "(SELECT COUNT(*) FROM orders o "
        "WHERE o.user_id=users.user_id) AS order_count "
        "FROM users "
        "ORDER BY created_at DESC"
    )

    return render_template(
        "admin/customers.html",
        customers=rows
    )


@bp.route(
    "/customers/<int:user_id>"
)
@admin_required
def customer_detail(user_id):

    customer = query(
        "SELECT * FROM users WHERE user_id=%s",
        (user_id,),
        one=True
    )

    if not customer:
        abort(404)

    orders = query(
        "SELECT * FROM orders "
        "WHERE user_id=%s "
        "ORDER BY created_at DESC",
        (user_id,)
    )

    return render_template(
        "admin/customer_detail.html",
        customer=customer,
        orders=orders
    )


@bp.post(
    "/customers/<int:user_id>/delete"
)
@admin_required
def customer_delete(user_id):

    execute(
        "DELETE FROM users WHERE user_id=%s",
        (user_id,)
    )

    flash(
        "Customer account removed.",
        "success"
    )

    return redirect(
        url_for("admin.customers")
    )


# ---------------- 6.0 Manage Orders ----------------
@bp.route("/orders")
@admin_required
def orders():

    rows = query(
        "SELECT o.*, "
        "u.name AS customer_name, "
        "pay.method AS payment_method, "
        "pay.status AS payment_status "
        "FROM orders o "
        "JOIN users u ON u.user_id=o.user_id "
        "LEFT JOIN payments pay "
        "ON pay.order_id=o.order_id "
        "ORDER BY o.created_at DESC"
    )

    return render_template(
        "admin/orders.html",
        orders=rows,
        statuses=ORDER_STATUSES
    )


@bp.route(
    "/orders/<int:order_id>"
)
@admin_required
def order_detail(order_id):

    order = query(
        "SELECT o.*, "
        "u.name AS customer_name, "
        "u.email "
        "FROM orders o "
        "JOIN users u "
        "ON u.user_id=o.user_id "
        "WHERE o.order_id=%s",

        (order_id,),
        one=True
    )

    if not order:
        abort(404)

    items = query(
        "SELECT oi.*, p.name "
        "FROM order_items oi "
        "JOIN products p "
        "ON p.product_id=oi.product_id "
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
        "admin/order_detail.html",
        order=order,
        items=items,
        payment=payment,
        statuses=ORDER_STATUSES,
        payment_statuses=PAYMENT_STATUSES
    )


@bp.post(
    "/orders/<int:order_id>/status"
)
@admin_required
def order_status(order_id):

    status = request.form.get("status")

    if status not in ORDER_STATUSES:
        abort(400)

    execute(
        "UPDATE orders SET status=%s "
        "WHERE order_id=%s",
        (status, order_id)
    )

    flash(
        f"Order marked as {status}.",
        "success"
    )

    return redirect(
        request.referrer
        or url_for("admin.orders")
    )


# ---------------- 7.0 Manage Payments ----------------
@bp.route("/payments")
@admin_required
def payments():

    rows = query(
        "SELECT pay.*, "
        "o.user_id, "
        "u.name AS customer_name, "
        "o.status AS order_status "
        "FROM payments pay "
        "JOIN orders o "
        "ON o.order_id=pay.order_id "
        "JOIN users u "
        "ON u.user_id=o.user_id "
        "ORDER BY pay.created_at DESC"
    )

    return render_template(
        "admin/payments.html",
        payments=rows,
        payment_statuses=PAYMENT_STATUSES
    )


@bp.post(
    "/payments/<int:payment_id>/status"
)
@admin_required
def payment_status(payment_id):

    status = request.form.get("status")

    if status not in PAYMENT_STATUSES:
        abort(400)

    execute(
        "UPDATE payments SET status=%s "
        "WHERE payment_id=%s",
        (status, payment_id)
    )

    flash(
        f"Payment marked as {status}.",
        "success"
    )

    return redirect(
        request.referrer
        or url_for("admin.payments")
    )


# ---------------- 8.0 Manage Contact Messages ----------------
@bp.route("/messages")
@admin_required
def messages():

    rows = query(
        "SELECT * FROM contact_messages "
        "ORDER BY created_at DESC"
    )

    return render_template(
        "admin/messages.html",
        messages=rows
    )


@bp.route(
    "/messages/<int:message_id>",
    methods=["GET", "POST"]
)
@admin_required
def message_detail(message_id):

    if request.method == "POST":

        reply = request.form.get(
            "admin_reply",
            ""
        ).strip()

        execute(
            "UPDATE contact_messages "
            "SET admin_reply=%s, status='Responded' "
            "WHERE message_id=%s",

            (reply, message_id)
        )

        flash(
            "Reply saved.",
            "success"
        )

        return redirect(
            url_for("admin.messages")
        )

    msg = query(
        "SELECT * FROM contact_messages "
        "WHERE message_id=%s",

        (message_id,),
        one=True
    )

    if not msg:
        abort(404)

    if msg["status"] == "New":

        execute(
            "UPDATE contact_messages "
            "SET status='Read' "
            "WHERE message_id=%s",

            (message_id,)
        )

    return render_template(
        "admin/message_detail.html",
        message=msg
    )