from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from db.db import SessionLocal
import jwt
from db.models import UserInDB
from utils.jwt_auth import create_access_token, create_refresh_token

from passlib.context import CryptContext


router = APIRouter()

class UserInfo(BaseModel):
    username: str
    email: str
    role: str

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
def login(email:str,password:str, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role},secret_key=settings.secret_key)
    refresh_token = create_refresh_token( data={"sub": user.email},secret_key=settings.secret_key)

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"message": "Login successful"}

@router.post('/refresh')
def refresh(response: Response, request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms="HS256")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    role = get_user_info(db, email=payload.get("sub")).role
    if not role:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = create_access_token(data={"sub": payload.get("sub"), "role": role },secret_key=settings.secret_key)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"message": "Token refreshed"}

@router.post('/logout')
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}


get_hash_password = lambda password: pwd_context.hash(password)

def get_user_hashed_password(db, email):
    try:
        user = db.query(UserInDB).filter(UserInDB.email == email).first()
        if not user:
            return None 
        return user.password
    except Exception as e:
        return None


def get_user_info(db, email):
    try:
        user = db.query(UserInDB).filter(UserInDB.email == email).first()
        if user:
            return UserInfo(username=user.username, email=user.email, role=user.role.role_name)
    except:
        return None
    return user

def authenticate_user(db, email: str, password: str):
    user_hashed_password = get_user_hashed_password(db, email)
    if not user_hashed_password:
        return False
    if not pwd_context.verify(password, user_hashed_password):
        return False
    return get_user_info(db, email)

def get_current_user(request: Request,db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms="HS256")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    
    return get_user_info(db, email=payload.get("sub"))


class CheckRole:
    def __init__(self, role: str):
        self.role = role

    def __call__(self, user: UserInfo = Depends(get_current_user)):
        if user.role != self.role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return True