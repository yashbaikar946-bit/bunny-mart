"""Creates the default admin row in D10 (admin)."""
from werkzeug.security import generate_password_hash
from app import create_app
from app.db import get_db

app = create_app()
with app.app_context():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT IGNORE INTO admin (username, password_hash) VALUES (%s, %s)",
        ("admin", generate_password_hash("admin123")),
    )
    db.commit()
    print("Admin ready -> username: admin / password: admin123")
