from pydantic import BaseModel
from enum import Enum
from fastapi import HTTPException
from db.models import UserInDB
from passlib.context import CryptContext
from db.db import SessionLocal

class Role(Enum):
    admin = 1
    user = 2

class User(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    role: Role



class UserInfo(BaseModel):
    username: str
    email: str
    role: Role

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        print(user.role)
        if user:
            return UserInfo(username=user.username, email=user.email, role=user.role_id)
    except Exception as e:
        print(e)
        return None
    return user

def register(user: User, db):
    try: 
        hashed_password = get_hash_password(user.password)
        if db.query(UserInDB).filter(UserInDB.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        db_user = UserInDB(username=user.username,email=user.email,role_id=user.role.value, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def delete(email, db):
    try:
        db_user = db.query(UserInDB).filter(UserInDB.email == email).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="User not found")
        db.delete(db_user)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def update(user: User, db):
    try:
        db_user = db.query(UserInDB).filter(UserInDB.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="User not found")
        db_user.first_name = user.first_name
        db_user.last_name = user.last_name
        db_user.username = user.username
        db_user.email = user.email
        db_user.role_id = user.role.value
        db_user.password = get_hash_password(user.password)
        db.commit()
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))