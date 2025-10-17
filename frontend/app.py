from flask import Flask, render_template, request, redirect, flash, url_for, session
import requests, os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devsecret")

API_AUTH = "http://localhost:8000/api/auth"
API_NOTES = "http://localhost:8000/api/notes"

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = {"username": request.form["username"], "password": request.form["password"]}
        response = requests.post(f"{API_AUTH}/login", data=data).json()
        if "error" in response:
            flash(response["error"], "danger")
            return redirect(url_for("login"))
        else:
            session["username"] = response["username"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = {
            "username": request.form["username"],
            "email": request.form["email"],
            "password": request.form["password"],
            "confirm_password": request.form["confirm_password"]
        }
        response = requests.post(f"{API_AUTH}/register", data=data).json()
        if "error" in response:
            flash(response["error"], "danger")
            return redirect(url_for("register"))
        else:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    username = session["username"]
    response = requests.get(f"{API_NOTES}/user/{username}").json()
    return render_template("dashboard.html", username=username, notes=response)

@app.route("/create_note", methods=["GET", "POST"])
def create_note():
    if "username" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        note_type = request.form["note_type"]
        data = {"username": session["username"], "note_type": note_type}

        files = None
        if note_type == "text":
            data["content"] = request.form["content"]
        else:
            files = {"file": request.files["file"]}

        response = requests.post(f"{API_NOTES}/create", data=data, files=files).json()
        if "error" in response:
            flash(response["error"], "danger")
        else:
            flash("Note created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_note.html")
