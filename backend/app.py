from flask import Flask, request, jsonify
import psycopg2
import os
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "notesdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

while True:
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        print("Connected to database")
        break

    except psycopg2.OperationalError:
        print("Database not ready, retrying...")
        time.sleep(2)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL
)
""")

conn.commit()


@app.route("/notes", methods=["GET"])
def get_notes():
    cur.execute("SELECT * FROM notes")
    rows = cur.fetchall()

    notes = []

    for row in rows:
        notes.append({
            "id": row[0],
            "content": row[1]
        })

    return jsonify(notes)


@app.route("/notes", methods=["POST"])
def add_note():
    data = request.json

    cur.execute(
        "INSERT INTO notes (content) VALUES (%s)",
        (data["content"],)
    )

    conn.commit()

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
