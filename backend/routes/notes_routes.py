from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Response
from backend.services.notes_service import save_note, get_notes, fs
from bson.objectid import ObjectId

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


@router.get("/file/{file_id}")
def download_file(file_id: str):
    try:
        oid = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file id")

    try:
        grid_out = fs.get(oid)
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")

    headers = {"Content-Disposition": f"attachment; filename=\"{grid_out.filename}\""}
    return Response(content=grid_out.read(), media_type=grid_out.content_type or "application/octet-stream", headers=headers)
