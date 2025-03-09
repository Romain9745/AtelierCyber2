from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from db.models import UserInDB
from routers.auth import CheckRole
from utils.users import UserInfo, get_db, register, delete, update, User, Role, ModifyUser
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/admin",dependencies=[Depends(CheckRole(Role.admin))])

class UserOut(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: str
    email: str
    role_id: Role
    last_login: datetime


@router.post('/create_user', status_code=201)
def create_user(user: User, db: Session = Depends(get_db)):
    new_user = register(user, db)
    return {"message": "User created", "user_id": new_user.id}

@router.get('/users', response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(UserInDB).all()
        for user in users:
            if user.last_login is None:
                user.last_login = user.created_at

        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching users")
    
@router.get('/user/{email}', response_model=UserOut)
def get_user(email: str, db: Session = Depends(get_db)):
    try:
        user = db.query(UserInDB).filter(UserInDB.email == email).first()
        if user:
            if user.last_login is None:
                user.last_login = user.created_at
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching user")

@router.post('/delete_user', status_code=204)
def delete_user(user: UserInfo, db: Session = Depends(get_db)):
    delete(user.email, db)
    return {"message": "User deleted"}

@router.post('/update_user')
def update_user(user: ModifyUser, db: Session = Depends(get_db)):
    updated_user = update(user, db)
    return {"message": "User updated", "user_id": updated_user.id}