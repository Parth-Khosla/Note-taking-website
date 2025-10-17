from fastapi import APIRouter, Form
from backend.services.auth_service import create_user, verify_user

router = APIRouter(prefix="/api/auth")

@router.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        return {"error": "Passwords do not match."}
    return create_user(username, email, password)

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return verify_user(username, password)
