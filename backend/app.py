```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import OperationalError
import os
import time

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "notesdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def wait_for_database():
    while True:
        try:
            conn = get_connection()
            conn.close()

            print("Connected to database")
            return

        except OperationalError:
            print("Database not ready, retrying...")
            time.sleep(2)


def init_database():
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL
            )
        """)

        conn.commit()
        cur.close()

    finally:
        conn.close()


@app.route("/notes", methods=["GET"])
def get_notes():
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("SELECT id, content FROM notes ORDER BY id")
        rows = cur.fetchall()

        notes = [
            {
                "id": row[0],
                "content": row[1]
            }
            for row in rows
        ]

        cur.close()

        return jsonify(notes)

    finally:
        conn.close()


@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json()

    if not data or "content" not in data:
        return jsonify({
            "error": "content is required"
        }), 400

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO notes (content) VALUES (%s)",
            (data["content"],)
        )

        conn.commit()
        cur.close()

        return jsonify({
            "status": "ok"
        }), 201

    finally:
        conn.close()


if __name__ == "__main__":
    wait_for_database()
    init_database()

    app.run(
        host="0.0.0.0",
        port=5000
    )
