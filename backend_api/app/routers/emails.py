from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.db import get_db
from db.models import MailsInDb, EmailAccountinDB, UserInDB
from routers.auth import get_current_user, CheckRole, Role
from utils.users import UserInfo
from typing import Annotated

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
def get_emails(user: Annotated[UserInfo, Depends(get_current_user)], db: Session = Depends(get_db)):
    try:
        results = db.query(MailsInDb.source, MailsInDb.recipient, MailsInDb.subject, MailsInDb.explanation).join(EmailAccountinDB, MailsInDb.recipient == EmailAccountinDB.email).join(UserInDB, EmailAccountinDB.added_by == UserInDB.id).filter(UserInDB.email == user.email, MailsInDb.is_phishing== True).all()
        if results:
            return [MailInfo(source=result.source, recipient=result.recipient, subject=result.subject, explanation=result.explanation) for result in results]
        else:
            return {"message ": "No blocked mails found for this user."}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/email_body')
def get_emails(source: str, recipient: str, subject: str, explanation: str,user: Annotated[UserInfo, Depends(get_current_user)], db: Session = Depends(get_db)):
    try:
        user_id = db.query(UserInDB.id).filter(UserInDB.email == user.email).first()
        account_linked = db.query(EmailAccountinDB).filter(EmailAccountinDB.email == recipient, EmailAccountinDB.added_by == user_id.id).first()
        if not account_linked:
            raise HTTPException(status_code=403, detail="You are not authorized to access this information")
        result = db.query(MailsInDb.email_body).filter(MailsInDb.source == source,MailsInDb.recipient == recipient,MailsInDb.subject == subject,MailsInDb.explanation == explanation).first()      
        if result:
            return MailBodyInfo(email_body=result.email_body)
        else:
            raise HTTPException(status_code=404, detail="No email body found")
    except HTTPException as http_exc:
        print(f"HTTP exception: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get('/email_uid')
def get_emails(source: str, recipient: str, subject: str, explanation: str,user: Annotated[UserInfo, Depends(get_current_user)], db: Session = Depends(get_db)):
    try:
        user_id = db.query(UserInDB.id).filter(UserInDB.email == user.email).first()
        account_linked = db.query(EmailAccountinDB).filter(EmailAccountinDB.email == recipient, EmailAccountinDB.added_by == user_id.id).first()
        if not account_linked and user.role != Role.admin:
            raise HTTPException(status_code=403, detail="You are not authorized to access this information")
        result = db.query(MailsInDb.id).filter(MailsInDb.source == source,MailsInDb.recipient == recipient,MailsInDb.subject == subject,MailsInDb.explanation == explanation).first()      
        if result:
            return MailUidInfo(email_uid=result.id)
        else:
            raise HTTPException(status_code=404, detail="No mail entry found")
    except HTTPException as http_exc:
        print(f"HTTP exception: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")