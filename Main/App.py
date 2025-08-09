import os
import json
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_this_secret")
bcrypt = Bcrypt(app)

USERS_FILE = "users.json"
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin123")  # set in env for security
PROTECTED_SCRIPT = """-- Protected Lua Script
print("Welcome to HanesArmor!")
game.Players.LocalPlayer.Character.Humanoid.WalkSpeed = 100
"""

def load_users():
    if not os.path.isfile(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def is_logged_in():
    return "username" in session

def is_admin():
    return session.get("is_admin", False)

@app.route("/")
def home():
    return render_template("index.html", logged_in=is_logged_in(), username=session.get("username"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in():
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()
        if username in users:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        users[username] = pw_hash
        save_users(users)
        flash("Registered successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()
        pw_hash = users.get(username)
        if pw_hash and bcrypt.check_password_hash(pw_hash, password):
            session["username"] = username
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("home"))

@app.route("/script")
def script():
    if not is_logged_in():
        flash("You need to log in to view the script.", "error")
        return redirect(url_for("login"))
    return render_template("script.html", script=PROTECTED_SCRIPT)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not is_logged_in():
        flash("Admin login required.", "error")
        return redirect(url_for("login"))
    if not is_admin():
        # simple admin login on this route
        if request.method == "POST":
            if request.form.get("admin_pass") == ADMIN_PASS:
                session["is_admin"] = True
                flash("Admin access granted.", "success")
                return redirect(url_for("admin"))
            else:
                flash("Incorrect admin password.", "error")
        return render_template("admin_login.html")
    
    users = load_users()
    if request.method == "POST":
        # Add user
        add_username = request.form.get("add_username", "").strip()
        add_password = request.form.get("add_password", "").strip()
        if add_username and add_password:
            if add_username in users:
                flash("User already exists.", "error")
            else:
                pw_hash = bcrypt.generate_password_hash(add_password).decode("utf-8")
                users[add_username] = pw_hash
                save_users(users)
                flash(f"User {add_username} added.", "success")
        # Remove user
        remove_username = request.form.get("remove_username", "").strip()
        if remove_username:
            if remove_username in users:
                del users[remove_username]
                save_users(users)
                flash(f"User {remove_username} removed.", "success")
            else:
                flash("User not found.", "error")
    return render_template("admin.html", users=users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
