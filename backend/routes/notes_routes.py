from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Response
import os
from backend.services.notes_service import save_note, get_notes, fs
from bson.objectid import ObjectId

router = APIRouter(prefix="/api/notes")


@router.post("/create")
def create_note(
    username: str = Form(...),
    note_type: str = Form(...),
    content: str = Form(None),
    title: str = Form(None),
    file: UploadFile = File(None)
):
    return save_note(username, note_type, content, file, title)


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

    # Try to find note metadata to get a better filename (with extension)
    from backend.services.notes_service import get_note_by_file_id
    note = get_note_by_file_id(file_id)
    filename_for_download = None
    if note:
        # prefer stored_filename, then original_filename, then gridfs filename
        filename_for_download = note.get("stored_filename") or note.get("original_filename")
    if not filename_for_download:
        filename_for_download = grid_out.filename or "download"

    # Ensure filename_for_download has an extension; try metadata from grid_out or note
    base, ext = os.path.splitext(filename_for_download)
    if not ext:
        # try GridFS metadata first
        meta_ext = None
        try:
            meta = grid_out.metadata or {}
            meta_ext = meta.get("extension")
        except Exception:
            meta_ext = None

        if not meta_ext and note:
            meta_ext = note.get("extension")

        if meta_ext:
            filename_for_download = f"{filename_for_download}.{meta_ext}" if not filename_for_download.endswith(f".{meta_ext}") else filename_for_download

    headers = {"Content-Disposition": f"attachment; filename=\"{filename_for_download}\""}
    return Response(content=grid_out.read(), media_type=grid_out.content_type or "application/octet-stream", headers=headers)
