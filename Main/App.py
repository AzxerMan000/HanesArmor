import os
import secrets
from flask import Flask, session, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", secrets.token_hex(32))

# Generate random key once on server start
ACCESS_KEY = secrets.token_hex(8)  # Example: '9f1c3a2d4b5e6f7a'

PROTECTED_SCRIPT = """-- Protected Lua Script
print("Welcome to the secret script!")
"""

@app.route("/get_key")
def get_key():
    # Show the generated key (for admin or users)
    return f"<h2>Your access key is: <code>{ACCESS_KEY}</code></h2>"

@app.route("/script", methods=["GET", "POST"])
def script():
    if request.method == "POST":
        entered_key = request.form.get("access_key", "")
        if entered_key == ACCESS_KEY:
            session["access_granted"] = True
            return redirect(url_for("script"))
        else:
            flash("Incorrect access key!", "error")
            return redirect(url_for("script"))

    if session.get("access_granted"):
        return render_template("script.html", script=PROTECTED_SCRIPT)
    else:
        return render_template("enter_key.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
