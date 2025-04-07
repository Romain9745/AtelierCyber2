from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.db import get_db
from db.models import MailsInDb, EmailAccountinDB, UserInDB

router = APIRouter(tags=["mails"])

class MailInfo(BaseModel):
    source: str
    recipient: str
    subject: str
    explanation: str
    
class MailBodyInfo(BaseModel):
    email_body: str
    
class MailUidInfo(BaseModel):
    email_uid: int

@router.get('/blocked_emails')
def get_emails(mail: str, db: Session = Depends(get_db)):
    print(mail)
    try:
        results = db.query(MailsInDb.source, MailsInDb.recipient, MailsInDb.subject, MailsInDb.explanation).join(EmailAccountinDB, MailsInDb.recipient == EmailAccountinDB.email).join(UserInDB, EmailAccountinDB.added_by == UserInDB.id).filter(UserInDB.email == mail).all()
        if results:
            return [MailInfo(source=result.source, recipient=result.recipient, subject=result.subject, explanation=result.explanation) for result in results]
        else:
            return {"message ": "No email entries found for this user."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/email_body')
def get_emails(source=str, recipient=str, subject=str, explanation=str, db: Session = Depends(get_db)):
    try:
        result = db.query(MailsInDb.email_body).filter(MailsInDb.source == source,MailsInDb.recipient == recipient,MailsInDb.subject == subject,MailsInDb.explanation == explanation).first()      
        if result:
            return MailBodyInfo(email_body=result.email_body)
        else:
            raise HTTPException(status_code=404, detail="No mail body entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/email_uid')
def get_emails(source=str, recipient=str, subject=str, explanation=str, db: Session = Depends(get_db)):
    try:
        result = db.query(MailsInDb.id).filter(MailsInDb.source == source,MailsInDb.recipient == recipient,MailsInDb.subject == subject,MailsInDb.explanation == explanation).first()      
        if result:
            return MailUidInfo(email_uid=result.id)
        else:
            raise HTTPException(status_code=404, detail="No mail entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))