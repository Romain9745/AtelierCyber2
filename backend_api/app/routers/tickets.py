from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from db.models import UserInDB, TicketInDB, EmailAccountinDB, MailsInDb
from routers.auth import CheckRole
from utils.users import UserInfo, register, delete, update, User, Role, ModifyUser
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from utils.db import get_db
from config import cipher
from utils.imap import send_email_to_inbox

# ,dependencies=[Depends(CheckRole(Role.admin))]
router = APIRouter(prefix="/tickets",tags=["Tickets"])

class TicketInfo(BaseModel):
    mail_uid: int
    user_mail: str
    state: int
    made_at: datetime
    last_modification_at: datetime
    
class StateInfo(BaseModel):
    mail_uid: int
    state: int
    last_modification_at: datetime

@router.get('/tickets')
def get_tickets(db: Session = Depends(get_db)):
    results = db.query(TicketInDB.mail_uid, TicketInDB.state, TicketInDB.made_at, TicketInDB.last_modification_at, UserInDB.email).join(UserInDB, TicketInDB.user_id == UserInDB.id).all()

    if not results:
        raise HTTPException(status_code=404, detail="No ticket entry found")

    try:
        return [TicketInfo(mail_uid=result.mail_uid, state=result.state, made_at=result.made_at, last_modification_at=result.last_modification_at, user_mail=result.email) for result in results]

    except Exception as e:
        print(f"Unexpected error: {e}")  # Debugging info
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post('/ticket')
def create_ticket(entry: TicketInfo, db: Session = Depends(get_db)):
    
    try:
        result = db.query(UserInDB.id).filter(UserInDB.email == entry.user_mail).first()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_entry = TicketInDB(mail_uid =entry.mail_uid, state=entry.state, made_at=entry.made_at, last_modification_at=entry.last_modification_at, user_id=result.id)
        db.add(new_entry)
        db.commit()
        return {"message": "Email ajouté à la liste des tickets"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/ticket_state')
def change_ticket_state(entry: StateInfo, db: Session = Depends(get_db)):
    
    try:        
        existing_entry = db.query(TicketInDB).filter_by(mail_uid=entry.mail_uid).first()
        if existing_entry:
            existing_entry.state = entry.state
            existing_entry.last_modification_at = entry.last_modification_at
            db.commit()
            
            if entry.state == 2:
                user = db.query(MailsInDb).filter_by(id=entry.mail_uid).first()
                imap_data=db.query(EmailAccountinDB).filter_by(email=user.recipient).first()
                imap_data.imap_password= cipher.decrypt(imap_data.imap_password.encode()).decode()
            
                send_email_to_inbox(imap_data.email, imap_data.imap_password, imap_data.imap_host, db, str(entry.mail_uid))
            return {"message": "Etat du ticket modifié"}
        else: 
            raise HTTPException(status_code=404,detail=f"L'entrée avec mail_uid {entry.mail_uid} n'a pas été trouvée.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    