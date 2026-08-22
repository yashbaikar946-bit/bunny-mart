"""Process 1.0 Register / Login / Forgot Password
Data store: D1 Users
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import query, execute

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 6:

            flash(
                "Name, email and a password of 6+ characters are required.",
                "error"
            )

            return render_template("customer/register.html")

        if query(
            "SELECT user_id FROM users WHERE email=%s",
            (email,),
            one=True
        ):

            flash(
                "That email is already registered.",
                "error"
            )

            return render_template("customer/register.html")

        execute(
            "INSERT INTO users "
            "(name, email, phone, address, password_hash) "
            "VALUES (%s,%s,%s,%s,%s)",
            (
                name,
                email,
                phone,
                address,
                generate_password_hash(password)
            ),
        )

        flash(
            "Registration successful. Please log in.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("customer/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = query(
            "SELECT * FROM users WHERE email=%s",
            (email,),
            one=True
        )

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session.clear()

            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]

            flash(
                "Logged in successfully.",
                "success"
            )

            return redirect(
                url_for("products.list_products")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template("customer/login.html")


# =========================================================
# FORGOT PASSWORD
# =========================================================

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        new_password = request.form.get(
            "new_password",
            ""
        )

        if not email or not phone or not new_password:

            flash(
                "All fields are required.",
                "error"
            )

            return render_template(
                "customer/forgot_password.html"
            )

        if len(new_password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return render_template(
                "customer/forgot_password.html"
            )

        user = query(
            "SELECT * FROM users "
            "WHERE email=%s AND phone=%s",
            (
                email,
                phone
            ),
            one=True
        )

        if not user:

            flash(
                "Email and phone number do not match.",
                "error"
            )

            return render_template(
                "customer/forgot_password.html"
            )

        execute(
            "UPDATE users SET password_hash=%s "
            "WHERE user_id=%s",
            (
                generate_password_hash(new_password),
                user["user_id"]
            )
        )

        flash(
            "Password changed successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "customer/forgot_password.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@bp.route("/logout")
def logout():

    session.pop("user_id", None)
    session.pop("user_name", None)

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("products.list_products")
    )
