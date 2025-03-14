from pydantic import BaseModel
from enum import Enum
from fastapi import HTTPException
from db.models import UserInDB, GlobalStatsinDB
from passlib.context import CryptContext
from datetime import datetime


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

class ModifyUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    role_id: Role



class UserInfo(BaseModel):
    username: str
    email: str
    role: Role



def modif_last_login(db, email):
    try:
        user = db.query(UserInDB).filter(UserInDB.email == email).first()
        if user:
            user.last_login = datetime.now()
            db.commit()
    except Exception as e:
        print(e)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

get_hash_password = lambda password: pwd_context.hash(password)

def get_user_hashed_password(db, email):
    try:
        user = db.query(UserInDB).filter(UserInDB.email == email).first()
        if not user:
            return None 
        return user.password
    except Exception as e:
        print(e)
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
        if db.query(UserInDB).filter(UserInDB.email == user.email).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        db_user = UserInDB(first_name=user.first_name,last_name=user.last_name,username=user.username,email=user.email,role_id=user.role.value, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.query(GlobalStatsinDB).first().total_users += 1
        db.commit()
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
        db.query(GlobalStatsinDB).first().total_users -= 1
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def update(user: ModifyUser, db):
    try:
        print(user)
        db_user = db.query(UserInDB).filter(UserInDB.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="User not found")
        db_user.first_name = user.first_name
        db_user.last_name = user.last_name
        db_user.username = user.username
        db_user.email = user.email
        db_user.role_id = user.role_id.value
        db.commit()
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))