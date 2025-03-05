from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from db.models import UserInDB
from routers.auth import CheckRole
from utils.users import UserInfo, get_hash_password, get_db, register, delete, update, User, Role




router = APIRouter(prefix="/admin",dependencies=[Depends(CheckRole(Role.admin))])



@router.post('/create_user', status_code=201)
def create_user(user: User, db: Session = Depends(get_db)):
    new_user = register(user, db)
    return {"message": "User created", "user_id": new_user.id}

@router.get('/users')
def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(UserInDB).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching users")

@router.post('/delete_user', status_code=204)
def delete_user(user: UserInfo, db: Session = Depends(get_db)):
    delete(user.email, db)
    return {"message": "User deleted"}

@router.post('/update_user')
def update_user(user: User, db: Session = Depends(get_db)):
    updated_user = update(user, db)
    return {"message": "User updated", "user_id": updated_user.id}