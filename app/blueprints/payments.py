import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, abort, current_app
)
from werkzeug.utils import secure_filename

from ..auth_utils import login_required
from ..db import query, execute

bp = Blueprint("payments", __name__, url_prefix="/payment")

ALLOWED = {"png", "jpg", "jpeg", "webp"}


def _order(order_id):
    order = query(
        "SELECT * FROM orders WHERE order_id=%s AND user_id=%s",
        (order_id, session["user_id"]),
        one=True
    )

    if not order:
        abort(404)

    return order


@bp.route("/<int:order_id>", methods=["GET", "POST"])
@login_required
def select(order_id):

    order = _order(order_id)

    if request.method == "POST":

        method = request.form.get("method")

        if method not in ("COD", "QR"):
            flash("Choose a payment method.", "error")
            return render_template(
                "customer/payment_select.html",
                order=order
            )

        # IMPORTANT:
        # Checkout page has already added Rs 300.
        # Do NOT add Rs 300 again here.

        total = float(order["total_amount"])

        existing = query(
            "SELECT * FROM payments WHERE order_id=%s",
            (order_id,),
            one=True
        )

        # COD
        if method == "COD":

            if existing:
                execute(
                    "UPDATE payments SET "
                    "method='COD', "
                    "status='Pending', "
                    "amount=%s, "
                    "proof_image=NULL "
                    "WHERE order_id=%s",
                    (total, order_id)
                )
            else:
                execute(
                    "INSERT INTO payments "
                    "(order_id, method, status, amount) "
                    "VALUES (%s, 'COD', 'Pending', %s)",
                    (order_id, total)
                )

            return redirect(
                url_for(
                    "orders.confirmation",
                    order_id=order_id
                )
            )

        # QR
        if existing:
            execute(
                "UPDATE payments SET "
                "method='QR', "
                "status='Pending', "
                "amount=%s "
                "WHERE order_id=%s",
                (total, order_id)
            )
        else:
            execute(
                "INSERT INTO payments "
                "(order_id, method, status, amount) "
                "VALUES (%s, 'QR', 'Pending', %s)",
                (order_id, total)
            )

        return redirect(
            url_for(
                "payments.qr",
                order_id=order_id
            )
        )

    return render_template(
        "customer/payment_select.html",
        order=order
    )


# ==========================================================
# QR PAYMENT
# ==========================================================

@bp.route("/<int:order_id>/qr", methods=["GET", "POST"])
@login_required
def qr(order_id):

    order = _order(order_id)

    # ------------------------------------------------------
    # GET ADMIN UPLOADED QR CODE
    # ------------------------------------------------------

    qr = query(
        "SELECT * FROM payment_qr_settings "
        "WHERE is_active=1 "
        "ORDER BY qr_id DESC "
        "LIMIT 1",
        one=True
    )

    # ------------------------------------------------------
    # PAYMENT PROOF UPLOAD
    # ------------------------------------------------------

    if request.method == "POST":

        file = request.files.get("proof")

        if not file or not file.filename:

            flash(
                "Please upload your payment screenshot.",
                "error"
            )

            return render_template(
                "customer/payment_qr.html",
                order=order,
                qr=qr
            )

        ext = file.filename.rsplit(".", 1)[-1].lower()

        if ext not in ALLOWED:

            flash(
                "Only PNG, JPG or WEBP images are accepted.",
                "error"
            )

            return render_template(
                "customer/payment_qr.html",
                order=order,
                qr=qr
            )

        fname = (
            f"proof_{order_id}_"
            f"{uuid.uuid4().hex[:8]}_"
            f"{secure_filename(file.filename)}"
        )

        file.save(
            os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                fname
            )
        )

        execute(
            "UPDATE payments SET "
            "proof_image=%s, "
            "status='Pending Verification' "
            "WHERE order_id=%s",
            (fname, order_id)
        )

        flash(
            "Payment proof uploaded. Awaiting admin verification.",
            "success"
        )

        return redirect(
            url_for(
                "orders.confirmation",
                order_id=order_id
            )
        )

    # ------------------------------------------------------
    # SHOW QR PAYMENT PAGE
    # ------------------------------------------------------

    return render_template(
        "customer/payment_qr.html",
        order=order,
        qr=qr
    )