from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from db.models import UserInDB, UserStatsinDB, TicketInDB, MailsInDb, EmailAccountinDB
from routers.auth import CheckRole
from utils.users import UserInfo, register, delete, update, User, Role, ModifyUser
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from utils.db import get_db
from utils.ticket import revoke_classification, TicketinfoToSend, StateInfo

router = APIRouter(prefix="/admin",dependencies=[Depends(CheckRole(Role.admin))],tags=["Admin"])

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
    new_stats = UserStatsinDB(user_id=new_user.id)
    try:
        db.add(new_stats)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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

@router.get('/tickets')
def get_tickets(db: Session = Depends(get_db)):
    results = db.query(TicketInDB.mail_uid, TicketInDB.state, TicketInDB.made_at, TicketInDB.last_modification_at, UserInDB.email).join(UserInDB, TicketInDB.user_id == UserInDB.id).all()

    if not results:
        raise HTTPException(status_code=404, detail="No ticket entry found")

    try:
        return [TicketinfoToSend(mail_uid=result.mail_uid, state=result.state, made_at=result.made_at, last_modification_at=result.last_modification_at, user_mail=result.email) for result in results]

    except Exception as e:
        print(f"Unexpected error: {e}")  # Debugging info
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post('/ticket_state')
def change_ticket_state(entry: StateInfo, db: Session = Depends(get_db)):
    try:        
        existing_entry = db.query(TicketInDB).filter_by(mail_uid=entry.mail_uid).first()
        if existing_entry:
            existing_entry.state = entry.state
            existing_entry.last_modification_at = datetime.now()
            db.commit()                
            
            if entry.state == 2:
                revoke_classification(entry, db)
            return {"message": "Etat du ticket modifié"}
        else: 
            raise HTTPException(status_code=404,detail=f"L'entrée avec mail_uid {entry.mail_uid} n'a pas été trouvée.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
