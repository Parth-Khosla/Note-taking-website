import io
from datetime import datetime
from backend.utils.db_connection import db
from gridfs import GridFS
from bson.objectid import ObjectId

notes_collection = db["notes"]
fs = GridFS(db)


def _read_file_bytes(file):
    """Attempt to read bytes from different kinds of file objects (FastAPI UploadFile, Werkzeug FileStorage, raw file-like)."""
    try:
        # Prefer file.file.read() for UploadFile/werkzeug FileStorage
        if hasattr(file, "file") and hasattr(file.file, "read"):
            return file.file.read()

        # Fallback: file.read() may be sync or async. If async, run it.
        if hasattr(file, "read") and callable(file.read):
            data = file.read()
            # If data is a coroutine (async read), run it to get bytes
            import inspect, asyncio
            if inspect.isawaitable(data):
                try:
                    return asyncio.run(data)
                except RuntimeError:
                    # If there's an event loop running, try to use it (best-effort)
                    loop = asyncio.get_event_loop()
                    return loop.run_until_complete(data)
            return data
    except Exception:
        pass
    return None


def _extract_text_from_docx(file_bytes):
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paragraphs)
    except Exception:
        return None


def _extract_text_from_pdf(file_bytes):
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(texts).strip() or None
    except Exception:
        return None


def save_note(username, note_type, content=None, file=None):
    note_data = {
        "username": username,
        "note_type": note_type,
        "timestamp": datetime.utcnow()
    }

    # Text-only notes
    if note_type == "text":
        note_data["content"] = content

    # File based notes: audio, file, image, video, pdf, docx etc.
    else:
        if not file:
            return {"error": "No file uploaded."}

        # Read bytes from supported file objects
        file_bytes = _read_file_bytes(file)
        if file_bytes is None:
            # try attribute .stream or .readable
            try:
                file_bytes = file.stream.read()
            except Exception:
                return {"error": "Unable to read uploaded file."}

        filename = getattr(file, "filename", None) or getattr(file, "name", None) or "upload"
        content_type = getattr(file, "content_type", None) or getattr(file, "mimetype", None) or "application/octet-stream"

        # store file in GridFS
        try:
            grid_out_id = fs.put(file_bytes, filename=filename, contentType=content_type)
        except Exception as e:
            return {"error": f"Failed to store file: {str(e)}"}

        note_data["file_id"] = grid_out_id
        note_data["filename"] = filename
        note_data["content_type"] = content_type

        # attempt lightweight conversions/extraction for searchable content
        lower = (filename or "").lower()
        if lower.endswith(".docx"):
            extracted = _extract_text_from_docx(file_bytes)
            if extracted:
                note_data["content"] = extracted
        elif lower.endswith(".pdf"):
            extracted = _extract_text_from_pdf(file_bytes)
            if extracted:
                note_data["content"] = extracted

    # insert into notes collection
    try:
        notes_collection.insert_one(note_data)
    except Exception as e:
        return {"error": f"Failed to save note metadata: {str(e)}"}

    return {"message": "Note saved successfully.", "file_id": str(note_data.get("file_id"))}


def get_notes(username):
    user_notes = list(notes_collection.find({"username": username}, {"_id": 0}))
    # Convert ObjectId to string for JSON responses where needed
    for n in user_notes:
        if "file_id" in n and isinstance(n["file_id"], ObjectId):
            n["file_id"] = str(n["file_id"])
    return user_notes
