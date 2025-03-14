from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.db import get_db
from db.models import MailsInDb

router = APIRouter(tags=["mails"])

class MailInfo(BaseModel):
    source: str
    recipient: str
    subject: str
    explanation: str
    
class MailBodyInfo(BaseModel):
    email_body: str

        
@router.get('/blocked_emails')
def get_emails(db: Session = Depends(get_db)):
    try:
        print("get_emails appelé")
        results = db.query(MailsInDb.source, MailsInDb.recipient, MailsInDb.subject, MailsInDb.explanation).all()
        print("les resultats sont ")
        print(results)
        if results:
            return [MailInfo(source=result.source, recipient=result.recipient, subject=result.subject, explanation=result.explanation) for result in results]
        else:
            raise HTTPException(status_code=404, detail="No blacklist entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/email_body')
def get_emails(source=str, recipient=str, subject=str, explanation=str, db: Session = Depends(get_db)):
    try:
        print("get_emails appelé")
        result = db.query(MailsInDb.email_body).filter(MailsInDb.source == source,MailsInDb.recipient == recipient,MailsInDb.subject == subject,MailsInDb.explanation == explanation).first()      
        print("les resultats sont ")
        print(result)
        if result:
            return MailBodyInfo(email_body=result.email_body)
        else:
            raise HTTPException(status_code=404, detail="No blacklist entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))