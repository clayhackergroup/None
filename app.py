from flask import Flask, request, jsonify, session, send_from_directory
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit
import sqlite3, os, re, html, threading, time

# ------------ App Setup ------------
app = Flask(__name__, static_folder="static")
bcrypt = Bcrypt(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Environment / Defaults
app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "babyclay")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Hacker1212#")
ADMIN_PHASEKEY = os.environ.get("ADMIN_PHASEKEY", "hahahahaha")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_PATH = "database.db"

# ------------ Database Setup ------------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
init_db()

def get_db():
    return sqlite3.connect(DB_PATH)

# ------------ Auto-cleanup Thread ------------
def delete_old_messages():
    """Deletes chat messages older than 48 hours to keep DB small."""
    while True:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""
                    DELETE FROM messages
                    WHERE created_at < datetime('now', '-48 hours')
                """)
                conn.commit()
                # optional vacuum to reclaim space
                conn.execute("VACUUM")
        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")
        time.sleep(6 * 60 * 60)  # run every 6 hours

threading.Thread(target=delete_old_messages, daemon=True).start()

# ------------ Helpers ------------
def valid_username(username: str) -> bool:
    return bool(re.match(r"^[A-Za-z0-9_.-]{3,32}$", username))

def sanitize(text: str) -> str:
    return html.escape(text)

# ------------ User Auth Routes ------------
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = data.get("password")
    confirm = data.get("confirm")

    if not (username and password and confirm):
        return jsonify(error="All fields required"), 400
    if password != confirm:
        return jsonify(error="Passwords do not match"), 400
    if not valid_username(username):
        return jsonify(error="Invalid username"), 400
    if len(password) < 8:
        return jsonify(error="Password too short"), 400

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    try:
        conn = get_db()
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()
        return jsonify(message="Registered successfully"), 200
    except sqlite3.IntegrityError:
        return jsonify(error="Username already taken"), 409

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = data.get("password")

    if not (username and password):
        return jsonify(error="Missing credentials"), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify(error="Invalid credentials"), 401

    user_id, uname, hashed_pw = row
    if bcrypt.check_password_hash(hashed_pw, password):
        session["user"] = {"id": user_id, "username": uname}
        return jsonify(message="Login successful"), 200
    return jsonify(error="Invalid credentials"), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify(message="Logged out"), 200

@app.route("/api/me")
def me():
    user = session.get("user")
    if user:
        return jsonify(user=user), 200
    return jsonify(user=None), 401

# ------------ Profile Update ------------
@app.route("/api/profile", methods=["POST"])
def update_profile():
    user = session.get("user")
    if not user:
        return jsonify(error="Not logged in"), 401
    data = request.get_json()
    nickname = (data.get("nickname") or "").strip()
    if not valid_username(nickname):
        return jsonify(error="Invalid nickname"), 400
    try:
        conn = get_db()
        conn.execute("UPDATE users SET username=? WHERE id=?", (nickname, user["id"]))
        conn.commit()
        conn.close()
        session["user"]["username"] = nickname
        return jsonify(message="Nickname updated"), 200
    except sqlite3.IntegrityError:
        return jsonify(error="Nickname already taken"), 409

# ------------ Chat System ------------
@socketio.on("connect")
def on_connect():
    user = session.get("user")
    if not user:
        return False
    emit("system", {"msg": f"{user['username']} joined the chat."}, broadcast=True)

@socketio.on("disconnect")
def on_disconnect():
    user = session.get("user")
    if user:
        emit("system", {"msg": f"{user['username']} left the chat."}, broadcast=True)

@socketio.on("message")
def handle_message(data):
    user = session.get("user")
    if not user:
        emit("error", {"msg": "You must be logged in."})
        return
    msg = (data.get("msg") or "").strip()
    if not msg:
        return
    safe_msg = sanitize(msg)
    conn = get_db()
    conn.execute("INSERT INTO messages (user_id, message) VALUES (?, ?)", (user["id"], safe_msg))
    conn.commit()
    conn.close()
    emit("chat", {"user": user["username"], "msg": safe_msg}, broadcast=True)

@app.route("/api/messages")
def get_messages():
    user = session.get("user")
    if not user:
        return jsonify(error="Not logged in"), 401
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.username, m.message, m.created_at
        FROM messages m
        JOIN users u ON m.user_id = u.id
        ORDER BY m.id DESC
        LIMIT 30
    """)
    rows = cur.fetchall()
    conn.close()
    messages = [{"user": r[0], "msg": r[1], "time": r[2]} for r in reversed(rows)]
    return jsonify(messages=messages), 200

# ------------ Admin: Auth + Posting ------------
@app.route("/admin/login", methods=["POST"])
@limiter.limit("6 per minute")
def admin_login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    phasekey = (data.get("phasekey") or "").strip()
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD or phasekey != ADMIN_PHASEKEY:
        return jsonify(error="Invalid admin credentials"), 401
    session["is_admin"] = True
    session["admin_user"] = ADMIN_USERNAME
    return jsonify(message="Admin authenticated"), 200

@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_user", None)
    return jsonify(message="Admin logged out"), 200

@app.route("/admin/post", methods=["POST"])
def admin_post():
    if not session.get("is_admin"):
        return jsonify(error="Not authorized"), 401
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    if not title or not content:
        return jsonify(error="Title and content required"), 400
    if len(title) > 200:
        return jsonify(error="Title too long"), 400
    if len(content) > 20000:
        return jsonify(error="Content too long"), 400
    safe_title = sanitize(title)
    safe_content = sanitize(content)
    author = session.get("admin_user", "admin")
    conn = get_db()
    conn.execute("INSERT INTO posts (author, title, content) VALUES (?, ?, ?)", (author, safe_title, safe_content))
    conn.commit()
    conn.close()
    return jsonify(message="Post published"), 200

@app.route("/api/posts", methods=["GET"])
def api_posts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, author, title, content, created_at
        FROM posts
        ORDER BY id DESC
        LIMIT 100
    """)
    rows = cur.fetchall()
    conn.close()
    posts = [{"id": r[0], "author": r[1], "title": r[2], "content": r[3], "time": r[4]} for r in rows]
    return jsonify(posts=posts), 200

# ------------ Static Files ------------
@app.route("/")
def home():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

# ------------ Run (port 8080 for onion) ------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=False)
