from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from db.models import UserInDB, TicketInDB, EmailAccountinDB, MailsInDb
from pydantic import BaseModel
from datetime import datetime
from utils.db import get_db
from routers.auth import get_current_user, Role
from typing import Annotated
from utils.users import UserInfo
from utils.ticket import revoke_classification,StateInfo, TicketinfoToSend


router = APIRouter(tags=["Tickets"])
    
class TicketInfo(BaseModel):
    mail_uid: int
    state: int
    user_explanation: str
    
class UserEmailInfo(BaseModel):
    user_mail: str
    
class MailInfo(BaseModel):
    source: str
    recipient: str
    subject: str
    email_body: str
    explanation: str
    user_explanation: str
    
@router.post('/ticket')
def create_ticket(entry: TicketInfo,user: Annotated[UserInfo, Depends(get_current_user)] ,db: Session = Depends(get_db)):
    try:
        user_id = db.query(UserInDB.id).filter(UserInDB.email == user.email).first()
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        mail = db.query(MailsInDb).filter(MailsInDb.id == entry.mail_uid).first()
        if not mail:
            raise HTTPException(status_code=404, detail="Mail not found")
        check_mail_account= db.query(EmailAccountinDB).filter(EmailAccountinDB.added_by == user_id.id,EmailAccountinDB.email==mail.recipient).first()
        if not check_mail_account:
            raise HTTPException(status_code=404, detail="Mail account not found")
        # Vérifier si le ticket existe déjà
        existing_ticket = db.query(TicketInDB).filter(TicketInDB.mail_uid == entry.mail_uid).first()
        if existing_ticket:
            raise HTTPException(status_code=400, detail="Ticket already exists")
        
        if user.role == Role.admin:
            new_entry = TicketInDB(mail_uid =entry.mail_uid, state=2,user_explanation=entry.user_explanation, made_at=datetime.now(), last_modification_at=datetime.now(), user_id=user_id.id)
            print(new_entry)
            db.add(new_entry)
            db.commit()
            revoke_classification(StateInfo(mail_uid=entry.mail_uid,state=2,last_modification_at=datetime.now()),db)
        else:
            new_entry = TicketInDB(mail_uid =entry.mail_uid, state=entry.state,user_explanation=entry.user_explanation, made_at=datetime.now(), last_modification_at=datetime.now(), user_id=user_id.id)
            db.add(new_entry)
            db.commit()
        return {"message": "Email ajouté à la liste des tickets"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/get_ticket_data')
def get_ticket_data(mail: str, state: int, date: str,user: Annotated[UserInfo, Depends(get_current_user)], db: Session = Depends(get_db)):
    try:
        # Vérifier si l'utilisateur existe
        user_id = db.query(UserInDB.id).filter(UserInDB.email == mail).first()
        if not user_id:
            print(f"No user found with email: {mail}")
            raise HTTPException(status_code=404, detail=f"No user found with email: {mail}")
        print(f"User ID found: {user_id.id}")

        #vérifier les droits de l'utilisateur
        if user.email != mail and user.role != Role.admin:
            print(f"User {user.email} does not have permission to access this data")
            raise HTTPException(status_code=403, detail="Permission denied")

        # Vérifier si le ticket existe
        ticket = db.query(TicketInDB.mail_uid,TicketInDB.user_explanation).filter(TicketInDB.user_id == user_id.id,TicketInDB.state == state,TicketInDB.last_modification_at == date).first()
        if not ticket:
            print(f"No ticket found for user ID: {user_id.id}, state: {state}, date: {date}")
            raise HTTPException(status_code=404, detail=f"No ticket found for the specified criteria")
        print(f"Mail UID found: {ticket.mail_uid}")

        # Vérifier si les informations du mail existent
        result = db.query(MailsInDb.source, MailsInDb.recipient, MailsInDb.subject, MailsInDb.email_body, MailsInDb.explanation).filter(MailsInDb.id == ticket.mail_uid).first()
        if not result:
            print(f"No mail entry found with ID: {ticket.mail_uid}")
            raise HTTPException(status_code=404, detail=f"No mail entry found with the specified ID")
        print(f"Mail entry found: {result}")

        # Retourner les données du mail
        return MailInfo(source=result.source,recipient=result.recipient,subject=result.subject,email_body=result.email_body,explanation=result.explanation,user_explanation=ticket.user_explanation)
    except HTTPException as http_exc:
        print(f"HTTP exception: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        # Gérer les erreurs imprévues
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
@router.get('/tickets')
def get_tickets(user: Annotated[UserInfo,Depends(get_current_user)],db: Session = Depends(get_db)):
    results = db.query(TicketInDB.mail_uid, TicketInDB.state, TicketInDB.made_at, TicketInDB.last_modification_at, UserInDB.email).join(UserInDB).filter(UserInDB.email == user.email).all()
    print(results,user.email)

    if not results:
        raise HTTPException(status_code=404, detail="No ticket entry found")

    try:
        return [TicketinfoToSend(mail_uid=result.mail_uid, state=result.state, made_at=result.made_at, last_modification_at=result.last_modification_at, user_mail=result.email) for result in results]

    except Exception as e:
        print(f"Unexpected error: {e}")  # Debugging info
        raise HTTPException(status_code=500, detail="Internal Server Error")


    