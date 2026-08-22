"""Processes 2.0 View Products, 3.0 Search Products, 4.0 View Product Details
Data stores: D2 Products, D3 Categories
"""
from flask import Blueprint, render_template, request, abort

from ..db import query

bp = Blueprint("products", __name__)


@bp.route("/")
def list_products():
    """2.0 View Products"""
    categories = query("SELECT * FROM categories ORDER BY name")
    products = query(
        "SELECT p.*, c.name AS category_name FROM products p "
        "LEFT JOIN categories c ON c.category_id = p.category_id "
        "ORDER BY p.created_at DESC"
    )
    return render_template(
        "customer/products.html",
        products=products,
        categories=categories,
        keyword="",
        category_id=None
    )


@bp.route("/search")
def search():
    """3.0 Search Products - keyword and/or category filter"""
    keyword = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)

    sql = (
        "SELECT p.*, c.name AS category_name FROM products p "
        "LEFT JOIN categories c ON c.category_id = p.category_id "
        "WHERE 1=1"
    )

    params = []

    if keyword:
        sql += " AND (p.name LIKE %s OR p.description LIKE %s)"
        params += [f"%{keyword}%", f"%{keyword}%"]

    if category_id:
        sql += " AND p.category_id = %s"
        params.append(category_id)

    sql += " ORDER BY p.name"

    products = query(sql, tuple(params))
    categories = query("SELECT * FROM categories ORDER BY name")

    return render_template(
        "customer/products.html",
        products=products,
        categories=categories,
        keyword=keyword,
        category_id=category_id
    )


@bp.route("/product/<int:product_id>")
def detail(product_id):
    """4.0 View Product Details"""

    product = query(
        "SELECT p.*, c.name AS category_name FROM products p "
        "LEFT JOIN categories c ON c.category_id = p.category_id "
        "WHERE p.product_id=%s",
        (product_id,),
        one=True
    )

    if not product:
        abort(404)

    return render_template(
        "customer/product_detail.html",
        product=product
    )