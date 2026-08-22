from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import OperationalError
import os
import time
import signal
import sys

app = Flask(__name__)

CORS(app, origins=[
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://nginx",
])

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "notesdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD environment variable is not set")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def wait_for_database(max_retries=30):
    for i in range(max_retries):
        try:
            conn = get_connection()
            conn.close()
            print("Connected to database")
            return True
        except OperationalError:
            print(f"Database not ready, retrying... ({i+1}/{max_retries})")
            time.sleep(2)
    return False


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


@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 503


@app.route("/notes", methods=["GET"])
def get_notes():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, content FROM notes ORDER BY id")
        rows = cur.fetchall()
        notes = [{"id": row[0], "content": row[1]} for row in rows]
        cur.close()
        return jsonify(notes)
    finally:
        conn.close()


@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({"error": "content is required"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (content) VALUES (%s)", (data["content"],))
        conn.commit()
        cur.close()
        return jsonify({"status": "ok"}), 201
    finally:
        conn.close()


def shutdown_handler(signum, frame):
    print("Shutting down gracefully...")
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)


if __name__ == "__main__":
    if not wait_for_database():
        print("Could not connect to database, exiting.")
        sys.exit(1)
    init_database()
    app.run(host="0.0.0.0", port=5000)
