from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.utils.schemas import UserCreate, Token
from src.database.utils.setup import get_db
from src.database.utils.models import User
from src.services.auth import hash_password, verify_password, create_access_token


auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@auth_router.post("/register/")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with a hashed password."""
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(username=user.username, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}


@auth_router.post("/login/", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    """Authenticate user and return a JWT token."""
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
