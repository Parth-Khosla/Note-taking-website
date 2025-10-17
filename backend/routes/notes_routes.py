from fastapi import APIRouter, Form, File, UploadFile
from backend.services.notes_service import save_note, get_notes

router = APIRouter(prefix="/api/notes")

@router.post("/create")
def create_note(
    username: str = Form(...),
    note_type: str = Form(...),
    content: str = Form(None),
    file: UploadFile = File(None)
):
    return save_note(username, note_type, content, file)

@router.get("/user/{username}")
def fetch_notes(username: str):
    return get_notes(username)
