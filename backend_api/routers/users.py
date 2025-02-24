from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from utils.db import SessionLocal
import jwt
from models import UserInDB
from jwt_auth import create_access_token, create_refresh_token

from passlib.context import CryptContext


router = APIRouter()

class User(BaseModel):
    username: str
    email: str
    password: str

class Settings(BaseModel):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expires: int = 30
    refresh_token_expires: int = 600

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = Settings()

@router.post('/login')
def login(username:str,password:str, response: Response, db: Session = Depends(get_db)):
    user = db.query(UserInDB).filter(UserInDB.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token({"sub": user.username, "role": user.role.role_name},settings.secret_key)
    refresh_token = create_refresh_token({"sub": user.username},settings.secret_key)

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"message": "Login successful"}

@router.post('/refresh')
def refresh(response: Response, request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    access_token = create_access_token({"sub": payload.get("sub"), "role": payload.get("role")},settings.secret_key)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"message": "Token refreshed"}

@router.post('/logout')
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}

@router.post('/register')
def register(user: User, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = UserInDB(username=user.username,email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

