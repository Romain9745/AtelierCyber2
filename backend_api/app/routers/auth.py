from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from db.db import SessionLocal
import jwt
from utils.jwt_auth import create_access_token, create_refresh_token
from utils.users import get_user_hashed_password, get_user_info, pwd_context, UserInfo, register, User, Role, modif_last_login
from utils.db import get_db
from db.models import UserInDB, UserStatsinDB




router = APIRouter(tags=["Auth"])

fake_User = User(first_name="John", last_name="Doe", username="johndoe", email="johndoe@gmail.com", password="password", role=Role.admin)
fake2 = User(first_name="John", last_name="Doe", username="johndoe", email="johndoe@gmail.com", password="password", role=Role.admin)
fake3 = User(first_name="Jane", last_name="Smith", username="janesmith",email="janesmith@example.com", password="password", role=Role.admin)

class LoginRequest(BaseModel):
    email: str
    password: str

class Settings(BaseModel):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expires: int = 30
    refresh_token_expires: int = 600





settings = Settings()
@router.post('/login')
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email, "role": user.role.name},secret_key=settings.secret_key)
    refresh_token = create_refresh_token( data={"sub": user.email},secret_key=settings.secret_key)

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    modif_last_login(db, user.email)

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
    
    role = get_user_info(db, email=payload.get("sub")).role.name
    if not role:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = create_access_token(data={"sub": payload.get("sub"), "role": role },secret_key=settings.secret_key)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"message": "Token refreshed"}

def get_current_user(request: Request,db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid access token")
    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms="HS256")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    
    return get_user_info(db, email=payload.get("sub"))

@router.post('/logout')
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}

@router.get('/me')
def me(user: UserInfo = Depends(get_current_user)):
    return user



def authenticate_user(db, email: str, password: str):
    user_hashed_password = get_user_hashed_password(db, email)
    if not user_hashed_password:
        return False
    print (pwd_context.verify(password, user_hashed_password))
    if not pwd_context.verify(password, user_hashed_password):
        return False
    return get_user_info(db, email)

@router.post('/first_admin_account')
def first_admin_account(user: User,db: Session = Depends(get_db)):
    is_User_Table_Empty = db.query(UserInDB).count() == 0
    if is_User_Table_Empty:
        user.role = Role.admin
        new_user = register(user, db)
        new_stats = UserStatsinDB(user_id=new_user.id)
        try:
            db.add(new_stats)
            db.commit()
            db.refresh(new_user)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return {"message": "First admin account created", "user_id": new_user.id}
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
    
def create_first_admin_account(db: Session):
    is_User_Table_Empty = db.query(UserInDB).count() == 0
    if is_User_Table_Empty:
        user = fake_User
        user.role = Role.admin
        new_user = register(user, db)
        new_stats = UserStatsinDB(user_id=new_user.id)
        try:
            db.add(new_stats)
            db.commit()
            db.refresh(new_user)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return {"message": "First admin account created", "user_id": new_user.id}
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

class CheckRole:
    def __init__(self, role: Role):
        self.role = role

    def __call__(self, user: UserInfo = Depends(get_current_user)):
        print(user.role)
        if user.role.name != self.role.name:
            raise HTTPException(status_code=403, detail="Forbidden")
        return True