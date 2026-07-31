from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)


@router.post("/register")
def register():
    return {
        "message": "User Registered"
    }


@router.post("/login")
def login():
    return {
        "access_token": "demo-token",
        "token_type": "bearer"
    }