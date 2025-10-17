import os
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.testclient import TestClient

from backend.main import app as fastapi_app
from frontend.app import app as flask_app

# Main FastAPI app
app = FastAPI(title="NoteVault Unified App")

# Mount backend
app.mount("/api", fastapi_app)

# Create TestClient for internal API calls
client = TestClient(app)
flask_app.config['TEST_CLIENT'] = client

# Mount frontend
app.mount("/", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("test:app", host="0.0.0.0", port=port, reload=True)
