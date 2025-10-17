import os
from datetime import datetime
from backend.utils.db_connection import db

notes_collection = db["notes"]

UPLOAD_DIR = "uploads"

def save_note(username, note_type, content=None, file=None):
    note_data = {
        "username": username,
        "note_type": note_type,
        "timestamp": datetime.utcnow()
    }

    if note_type == "text":
        note_data["content"] = content
    elif note_type == "audio" or note_type == "file":
        if not file:
            return {"error": "No file uploaded."}
        file_path = os.path.join(UPLOAD_DIR, note_type, file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        note_data["file_path"] = file_path

    notes_collection.insert_one(note_data)
    return {"message": "Note saved successfully."}

def get_notes(username):
    user_notes = list(notes_collection.find({"username": username}, {"_id": 0}))
    return user_notes
