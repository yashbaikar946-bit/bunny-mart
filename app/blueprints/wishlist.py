"""Process 5.0 Manage Wishlist (data store: D4 Wishlist, reads D2 Products)"""

from flask import Blueprint, render_template, redirect, url_for, session, flash

from ..auth_utils import login_required
from ..db import query, execute


bp = Blueprint("wishlist", __name__, url_prefix="/wishlist")


@bp.route("/")
@login_required
def view():
    items = query(
        "SELECT w.wishlist_id, p.* "
        "FROM wishlist w "
        "JOIN products p ON p.product_id = w.product_id "
        "WHERE w.user_id=%s "
        "ORDER BY w.added_at DESC",
        (session["user_id"],)
    )

    return render_template(
        "customer/wishlist.html",
        items=items
    )


@bp.post("/add/<int:product_id>")
@login_required
def add(product_id):

    # Check product exists
    product = query(
        "SELECT product_id FROM products WHERE product_id=%s",
        (product_id,),
        one=True
    )

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products.list_products"))

    # Add to wishlist only if not already present
    existing = query(
        "SELECT wishlist_id FROM wishlist "
        "WHERE user_id=%s AND product_id=%s",
        (session["user_id"], product_id),
        one=True
    )

    if existing:
        flash("Product is already in your wishlist.", "error")
    else:
        execute(
            "INSERT INTO wishlist (user_id, product_id) "
            "VALUES (%s,%s)",
            (session["user_id"], product_id)
        )
        flash("Added to wishlist.", "success")

    return redirect(url_for("wishlist.view"))


@bp.post("/remove/<int:product_id>")
@login_required
def remove(product_id):

    execute(
        "DELETE FROM wishlist "
        "WHERE user_id=%s AND product_id=%s",
        (session["user_id"], product_id)
    )

    flash("Removed from wishlist.", "success")

    return redirect(url_for("wishlist.view"))