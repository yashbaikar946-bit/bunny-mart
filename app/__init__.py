import os
from dotenv import load_dotenv
from flask import Flask

from .db import close_db


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.teardown_appcontext(close_db)

    # Customer Level 1 processes 1.0 - 11.0
    from .blueprints.auth import bp as auth_bp            # 1.0
    from .blueprints.products import bp as products_bp    # 2.0 3.0 4.0
    from .blueprints.wishlist import bp as wishlist_bp    # 5.0
    from .blueprints.cart import bp as cart_bp            # 6.0
    from .blueprints.orders import bp as orders_bp        # 7.0 9.0
    from .blueprints.payments import bp as payments_bp    # 8.0
    from .blueprints.profile import bp as profile_bp      # 10.0
    from .blueprints.contact import bp as contact_bp      # 11.0
    # Admin Level 1 processes 1.0 - 8.0
    from .blueprints.admin import bp as admin_bp

    for bp in (auth_bp, products_bp, wishlist_bp, cart_bp, orders_bp,
               payments_bp, profile_bp, contact_bp, admin_bp):
        app.register_blueprint(bp)

    @app.context_processor
    def inject_user():
        from flask import session
        return {"session_user": session.get("user_name"),
                "session_admin": session.get("admin_username")}

    return app
