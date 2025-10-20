from flask import Flask, render_template, request, redirect, flash, url_for, session
import requests, os
from dotenv import load_dotenv


load_dotenv()  # loads variables from .env into os.environ
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devsecret")
#print(app.secret_key) #used for debugging

#Replace the following accordingly

'''
Use this for local runnings
API_AUTH = "http://localhost:8000/api/auth"
API_NOTES = "http://localhost:8000/api/notes"
'''
"""
replace with domain name where the backend is running
API_AUTH = "domain name/api/auth"
API_NOTES = "domain name/api/notes"
"""

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")
#print(API_BASE) #used for debugging
API_AUTH = f"{API_BASE}/api/auth"
API_NOTES = f"{API_BASE}/api/notes"

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
    # Support pagination and sorting. Default page=1, per_page=10, sort=desc
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    sort = request.args.get('sort', 'desc')
    resp = requests.get(f"{API_NOTES}/user/{username}", params={"page": page, "per_page": per_page, "sort": sort})
    response = resp.json()
    # Add file_url for notes that have a file_id so templates can directly link to backend download
    notes = []
    total = 0
    page = int(page)
    per_page = int(per_page)
    sort = sort
    if isinstance(response, dict) and 'notes' in response:
        notes = response.get('notes', [])
        total = response.get('total', 0)
    else:
        # fallback for older API behavior
        notes = response

    for n in notes:
        if isinstance(n, dict) and n.get("file_id"):
            n["file_url"] = f"{API_NOTES}/file/{n['file_id']}"

    return render_template("dashboard.html", username=username, notes=notes, total=total, page=page, per_page=per_page, sort=sort)


@app.route('/notes/search')
def notes_search():
    if 'username' not in session:
        return {"error": "Not authenticated"}, 401
    username = session['username']
    q = request.args.get('q', '')
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    sort = request.args.get('sort', 'desc')
    resp = requests.get(f"{API_NOTES}/search/{username}", params={"q": q, "page": page, "per_page": per_page, "sort": sort})
    data = resp.json()

    # Normalize to {notes: [...], total, page, per_page}
    notes = []
    total = 0
    page_num = int(page)
    per_page_num = int(per_page)
    if isinstance(data, dict) and 'notes' in data:
        notes = data.get('notes') or []
        total = data.get('total', 0)
        page_num = data.get('page', page_num)
        per_page_num = data.get('per_page', per_page_num)
    elif isinstance(data, list):
        notes = data

    # add file_url where applicable
    for n in notes:
        if isinstance(n, dict) and n.get('file_id'):
            n['file_url'] = f"{API_NOTES}/file/{n['file_id']}"

    return {"notes": notes, "total": total, "page": page_num, "per_page": per_page_num}


@app.route('/notes/<note_id>', methods=['DELETE'])
def notes_delete(note_id):
    if 'username' not in session:
        return {"error": "Not authenticated"}, 401
    resp = requests.delete(f"{API_NOTES}/{note_id}")
    if resp.status_code != 200:
        return {"error": resp.text}, resp.status_code
    return {"message": "deleted"}

@app.route("/create_note", methods=["GET", "POST"])
def create_note():
    if "username" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        note_type = request.form["note_type"]
        data = {"username": session["username"], "note_type": note_type, "title": request.form.get("title")}

        files = None
        if note_type == "text":
            data["content"] = request.form.get("content")
        else:
            uploaded = request.files.get("file")
            if uploaded:
                import io
                # Read raw bytes to ensure binary content is preserved (avoid text-mode streams)
                uploaded_bytes = uploaded.read()
                files = {"file": (uploaded.filename, io.BytesIO(uploaded_bytes), uploaded.mimetype)}
            else:
                files = None

        response = requests.post(f"{API_NOTES}/create", data=data, files=files).json()
        if "error" in response:
            flash(response["error"], "danger")
        else:
            flash("Note created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_note.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
