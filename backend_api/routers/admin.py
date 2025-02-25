from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.db import SessionLocal
from db.models import UserInDB
from passlib.context import CryptContext
from routers.auth import UserInfo
from routers.auth import CheckRole,get_hash_password, get_db


router = APIRouter(prefix="/admin",dependencies=[Depends(CheckRole("admin"))])


@router.post('/create_user')
def register(user: UserInfo, db: Session = Depends(get_db)):
    hashed_password = get_hash_password(user.password)
    if user.role == "admin":
        role = 1
    else:
        role = 2
    if db.query(UserInDB).filter(UserInDB.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = UserInDB(username=user.username,email=user.email,role_id=role, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user