from flask import Flask, request, jsonify, Response
import psycopg2
from psycopg2 import OperationalError
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

import os
import time


app = Flask(__name__)


DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "notesdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")


if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD environment variable is not set")


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def wait_for_database(max_retries=30, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            conn = get_connection()
            conn.close()

            print("Connected to database", flush=True)

            return

        except OperationalError as error:
            print(
                f"Database not ready "
                f"({attempt}/{max_retries}): {error}",
                flush=True
            )

            time.sleep(delay)

    raise RuntimeError(
        "Could not connect to database after multiple attempts"
    )


def init_database():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL
                )
            """)

        conn.commit()

        print("Database initialized", flush=True)

    finally:
        conn.close()


@app.before_request
def ensure_database_ready():
    if not getattr(app, "_database_initialized", False):
        wait_for_database()
        init_database()

        app._database_initialized = True


@app.after_request
def record_request(response):
    if request.path != "/metrics":
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()

    return response


@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_connection()
        conn.close()

        return jsonify({
            "status": "ok",
            "database": "connected"
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "database": str(error)
        }), 503


@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


@app.route("/notes", methods=["GET"])
def get_notes():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, content FROM notes ORDER BY id"
            )

            rows = cur.fetchall()

        notes = [
            {
                "id": row[0],
                "content": row[1]
            }
            for row in rows
        ]

        return jsonify(notes)

    finally:
        conn.close()


@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json(silent=True)

    if not data or "content" not in data:
        return jsonify({
            "error": "content is required"
        }), 400


    content = data["content"].strip()


    if not content:
        return jsonify({
            "error": "content cannot be empty"
        }), 400


    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO notes (content)
                VALUES (%s)
                RETURNING id
                """,
                (content,)
            )

            note_id = cur.fetchone()[0]

        conn.commit()

        return jsonify({
            "id": note_id,
            "content": content
        }), 201

    finally:
        conn.close()
