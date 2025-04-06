from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from db.models import UserInDB, TicketInDB, EmailAccountinDB, MailsInDb
from pydantic import BaseModel
from datetime import datetime
from utils.db import get_db


# ,dependencies=[Depends(CheckRole(Role.admin))]
router = APIRouter(tags=["Tickets"])

class TicketinfoToSend(BaseModel):
    mail_uid: int
    user_mail: str
    state: int
    made_at: datetime
    last_modification_at: datetime
    
class TicketInfo(BaseModel):
    mail_uid: int
    user_mail: str
    state: int
    user_explanation: str
    
class StateInfo(BaseModel):
    mail_uid: int
    state: int
    last_modification_at: datetime
    
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
def create_ticket(entry: TicketInfo, db: Session = Depends(get_db)):
    try:
        result = db.query(UserInDB.id).filter(UserInDB.email == entry.user_mail).first()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_entry = TicketInDB(mail_uid =entry.mail_uid, state=entry.state,user_explanation=entry.user_explanation, made_at=datetime.now(), last_modification_at=datetime.now(), user_id=result.id)
        db.add(new_entry)
        db.commit()
        return {"message": "Email ajouté à la liste des tickets"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/get_ticket_data')
def get_ticket_data(mail: str, state: int, date: str, db: Session = Depends(get_db)):
    try:
        # Vérifier si l'utilisateur existe
        user_id = db.query(UserInDB.id).filter(UserInDB.email == mail).first()
        if not user_id:
            print(f"No user found with email: {mail}")
            raise HTTPException(status_code=404, detail=f"No user found with email: {mail}")
        print(f"User ID found: {user_id.id}")

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

    
@router.get('/get_mail_user')
def get_emails(mail: str, db: Session = Depends(get_db)):
    try:
        print(f"Received mail: {mail}")

        user_id = db.query(EmailAccountinDB.added_by).filter(EmailAccountinDB.email == mail).first()
        if user_id:
            print(f"User ID found for mail '{mail}': {user_id.added_by}")  # Log de user_id

            user_email = db.query(UserInDB.email).filter(UserInDB.id == user_id.added_by).first()
            if user_email:
                print(f"User email found for User ID '{user_id.added_by}': {user_email.email}")  # Log de l'email utilisateur
                return UserEmailInfo(user_mail=user_email.email)
            else:
                print(f"No user entry found for User ID '{user_id.added_by}'")  # Log si l'utilisateur n'est pas trouvé
                raise HTTPException(status_code=404, detail="No user entry found")
        else:
            print(f"No account entry found for mail '{mail}'")  # Log si le compte n'est pas trouvé
            raise HTTPException(status_code=404, detail="No account entry found")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    