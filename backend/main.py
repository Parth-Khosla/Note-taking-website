from fastapi import FastAPI
from backend.routes import auth_routes, notes_routes

app = FastAPI(title="NoteVault API")

app.include_router(auth_routes.router)
app.include_router(notes_routes.router)

# For testing: run `uvicorn backend.main:app --reload --port 8000`
