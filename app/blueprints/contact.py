"""Process 11.0 Contact Shop (data store: D9 Contact Messages)"""
from flask import Blueprint, render_template, request, session, flash, redirect, url_for

from ..db import execute

bp = Blueprint("contact", __name__, url_prefix="/contact")


@bp.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:100]
        email = request.form.get("email", "").strip()[:150]
        subject = request.form.get("subject", "").strip()[:150]
        message = request.form.get("message", "").strip()[:1000]
        if not name or not email or not message:
            flash("Name, email and message are required.", "error")
        else:
            execute("INSERT INTO contact_messages (user_id, name, email, subject, message) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (session.get("user_id"), name, email, subject, message))
            flash("Thanks for your message. Bunny Mart will get back to you.", "success")
            return redirect(url_for("contact.form"))
    return render_template("customer/contact.html")
