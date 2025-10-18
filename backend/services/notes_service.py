import io
import os
import mimetypes
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


def save_note(username, note_type, content=None, file=None, title=None):
    note_data = {
        "username": username,
        "note_type": note_type,
        "timestamp": datetime.utcnow()
    }

    if title:
        note_data["title"] = title

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

        # ensure filename has an extension; if not, try to infer from content_type
        base, ext = os.path.splitext(filename)
        if not ext:
            guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
            if guessed:
                filename = f"{filename}{guessed}"

        # store original filename and extension for later use
        _, ext = os.path.splitext(filename)
        note_data["original_filename"] = getattr(file, "filename", filename)
        note_data["extension"] = ext.lstrip('.') if ext else ''

        # store file in GridFS
        try:
            # Store file into GridFS. Include original filename and extension in metadata so
            # downloads can use the proper filename and extension.
            grid_out_id = fs.put(
                file_bytes,
                filename=filename,
                metadata={
                    "original_filename": getattr(file, "filename", filename),
                    "extension": note_data.get("extension", ""),
                    "content_type": content_type,
                },
            )
        except Exception as e:
            return {"error": f"Failed to store file: {str(e)}"}

        # If GridFS filename lacks extension, attempt to re-store the file with an inferred extension
        # so the file document stored in GridFS has a proper filename (some clients send unnamed blobs).
        base, ext = os.path.splitext(filename)
        if not ext:
            # infer extension from metadata or content-type
            inferred = note_data.get("extension")
            if not inferred:
                inferred = mimetypes.guess_extension(content_type.split(";")[0].strip())
                if inferred and inferred.startswith('.'):
                    inferred = inferred.lstrip('.')

            if inferred:
                new_filename = f"{filename}.{inferred}" if not filename.endswith(f".{inferred}") else filename
                try:
                    # Read original from GridFS and re-put with new filename
                    original = fs.get(grid_out_id)
                    new_id = fs.put(original.read(), filename=new_filename, metadata=original.metadata or {})
                    try:
                        fs.delete(grid_out_id)
                    except Exception:
                        pass
                    grid_out_id = new_id
                    filename = new_filename
                except Exception:
                    # if re-put fails, fall back to leaving original as-is but we keep metadata
                    pass

        note_data["file_id"] = grid_out_id
        note_data["filename"] = filename
        note_data["content_type"] = content_type
        note_data["stored_filename"] = filename

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


def get_note_by_file_id(file_id):
    """Return the note document (without _id) matching a GridFS file_id if present."""
    try:
        oid = ObjectId(file_id)
    except Exception:
        return None
    doc = notes_collection.find_one({"file_id": oid}, {"_id": 0})
    return doc
