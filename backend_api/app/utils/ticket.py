from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.models import MailsInDb, EmailAccountinDB, TicketInDB
from utils.imap import send_email_to_inbox
from config import cipher


class TicketinfoToSend(BaseModel):
    mail_uid: int
    user_mail: str
    state: int
    made_at: datetime
    last_modification_at: datetime
    
class StateInfo(BaseModel):
    mail_uid: int
    state: int
    last_modification_at: datetime

def revoke_classification(entry: StateInfo, db: Session):
    try:
            existing_mail = db.query(MailsInDb).filter_by(id=entry.mail_uid).first()
            existing_mail.explanation = "This email has been removed from the phishing folder by an administrator."
            existing_mail.is_phishing = False
            db.commit()
                
            user = db.query(MailsInDb).filter_by(id=entry.mail_uid).first()
            imap_data=db.query(EmailAccountinDB).filter_by(email=user.recipient).first()
            imap_password= cipher.decrypt(imap_data.imap_password.encode()).decode()
            
            send_email_to_inbox(imap_data.email, imap_password, imap_data.imap_host, db, str(entry.mail_uid))   
    except Exception as e:
        print(f"Error moving email to inbox: {e}")

