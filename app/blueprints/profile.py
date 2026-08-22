"""Process 10.0 Manage Profile (data store: D1 Users)"""

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for
)

from werkzeug.security import generate_password_hash, check_password_hash

from ..auth_utils import login_required
from ..db import query, execute


bp = Blueprint("profile", __name__, url_prefix="/profile")


# =========================================================
# VIEW / UPDATE PROFILE
# =========================================================

@bp.route("/", methods=["GET", "POST"])
@login_required
def view():

    user_id = session["user_id"]

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not email:

            flash(
                "Name and email are required.",
                "error"
            )

        else:

            clash = query(
                "SELECT user_id FROM users "
                "WHERE email=%s AND user_id<>%s",
                (email, user_id),
                one=True
            )

            if clash:

                flash(
                    "That email belongs to another account.",
                    "error"
                )

            else:

                execute(
                    "UPDATE users "
                    "SET name=%s, email=%s, phone=%s, address=%s "
                    "WHERE user_id=%s",
                    (
                        name,
                        email,
                        phone,
                        address,
                        user_id
                    )
                )

                session["user_name"] = name

                flash(
                    "Profile updated.",
                    "success"
                )

                return redirect(
                    url_for("profile.view")
                )

    user = query(
        "SELECT * FROM users WHERE user_id=%s",
        (user_id,),
        one=True
    )

    return render_template(
        "customer/profile.html",
        user=user
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    user_id = session["user_id"]

    if request.method == "POST":

        current_password = request.form.get(
            "current_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # Get current password hash
        user = query(
            "SELECT password_hash FROM users "
            "WHERE user_id=%s",
            (user_id,),
            one=True
        )

        if not user:

            flash(
                "User account not found.",
                "error"
            )

            return redirect(
                url_for("profile.view")
            )

        # Check current password
        if not check_password_hash(
            user["password_hash"],
            current_password
        ):

            flash(
                "Current password is incorrect.",
                "error"
            )

            return render_template(
                "customer/change_password.html"
            )

        # Check new password length
        if len(new_password) < 6:

            flash(
                "New password must be at least 6 characters.",
                "error"
            )

            return render_template(
                "customer/change_password.html"
            )

        # Check confirmation
        if new_password != confirm_password:

            flash(
                "New passwords do not match.",
                "error"
            )

            return render_template(
                "customer/change_password.html"
            )

        # Update password
        execute(
            "UPDATE users "
            "SET password_hash=%s "
            "WHERE user_id=%s",
            (
                generate_password_hash(new_password),
                user_id
            )
        )

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            url_for("profile.view")
        )

    return render_template(
        "customer/change_password.html"
    )