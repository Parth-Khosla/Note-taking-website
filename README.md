# 🗒️ NoteVault — Flask + FastAPI Based Note-Taking App (MongoDB)

## 📘 Overview
**NoteVault** is a web-based note-taking application built using **Flask** (for frontend & session management) and **FastAPI** (for backend API handling).  
It allows users to:
- ✍️ Create and manage **text notes**
- 🎙️ Record and store **audio notes**
- 📎 Upload **files** like PDFs and images
- 🔑 Register and log in securely
- 💾 Maintain session persistence (stay logged in until logout)

The app uses **MongoDB** for data storage, and environment variables are used for sensitive configurations.

---

## 🗂️ Project Directory Structure

```
NoteVault/
│
├── app.py                         # Flask entry point – handles routes, sessions, and template rendering
├── fastapi_app.py                 # FastAPI backend – manages database operations via REST APIs
├── db_connection.py               # Handles MongoDB connection setup using .env credentials
├── requirements.txt               # Lists Python dependencies
├── .env                           # Stores MongoDB URI, secret key, and other private config
│
├── templates/                     # HTML templates for frontend pages
│   ├── index.html                 # Landing page linking to login/signup
│   ├── login.html                 # Login form page (username + password)
│   ├── signup.html                # Signup page (username, email, password, confirm password)
│   ├── dashboard.html             # Main user dashboard to create and view notes
│
├── static/                        # Contains static assets like CSS and JS files
│   ├── css/                       # Stylesheets
│   ├── js/                        # Frontend scripts (optional)
│
├── uploads/                       # Stores user-uploaded files (audio, PDFs, images, etc.)
│
└── utils/
    ├── session_helper.py          # Helper functions for managing Flask session persistence
    └── validators.py              # Input validation and password verification logic
```

---

## ⚙️ Environment Configuration (`.env`)

Store sensitive data in an `.env` file at the project root:

```bash
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/<database>
SECRET_KEY=some-secret-key
UPLOAD_DIR=uploads
```

> ⚠️ Never commit your `.env` file to GitHub. Keep it private.

---

## 🧩 Basic Function of Each File

| File | Purpose |
|------|----------|
| `app.py` | Main Flask app file handling routes, sessions, and page rendering |
| `fastapi_app.py` | Backend API logic for note storage, login/signup, and database operations |
| `db_connection.py` | Creates a MongoDB client using credentials from `.env` |
| `requirements.txt` | Lists dependencies required to run the project |
| `.env` | Holds environment variables like DB URI and Flask secret key |
| `templates/index.html` | Homepage linking to login/signup routes |
| `templates/login.html` | Login form for registered users |
| `templates/signup.html` | Registration page for new users |
| `templates/dashboard.html` | Main user dashboard for note creation & file uploads |
| `static/css/` | Stylesheets for page design |
| `static/js/` | Optional scripts for interactivity |
| `uploads/` | Directory for storing uploaded user files |
| `utils/session_helper.py` | Functions for managing Flask sessions and user authentication states |
| `utils/validators.py` | Basic form and password validation utilities |

---

## 🚀 Next Steps
- [ ] Implement user signup/login routes in Flask  
- [ ] Create FastAPI endpoints for note creation & file upload  
- [ ] Integrate Flask frontend with FastAPI backend  
- [ ] Add note listing, editing, and deletion  
- [ ] Improve UI/UX for the dashboard  

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | Flask (HTML + Jinja Templates) |
| **Backend** | FastAPI |
| **Database** | MongoDB (Atlas) |
| **Auth & Sessions** | Flask Sessions |
| **Environment Management** | python-dotenv |
| **File Uploads** | Flask Uploads / Werkzeug |

---

## 🧪 Test MongoDB Connection

To verify your `.env` setup, create a simple test script:

```python
# quick_test.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
print(client.list_database_names())
```

Run:
```bash
python quick_test.py
```

If you see your database list printed, your MongoDB connection works ✅

---

## 📄 License
This project is open-source under the **MIT License**.

---

## ✨ Author
**Parth**  
🎓 Computer Science Student specializing in Cloud Computing  
💬 Loves building full-stack cloud-integrated apps with automation and analytics.
