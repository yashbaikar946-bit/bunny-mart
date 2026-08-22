"""MySQL connection helper. All DFD data stores D1..D10 live here."""
import os
import mysql.connector
from flask import g


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DB", "bunny_mart"),
            autocommit=False,
        )
    return g.db


def query(sql, params=(), one=False):
    cur = get_db().cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, params=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
