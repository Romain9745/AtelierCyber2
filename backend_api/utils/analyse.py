from datetime import datetime
from pydantic import BaseModel
import httpx
from db.models import WhitelistInDb, BlacklistInDb,EmailAccountinDB
from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db.db import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Email(BaseModel):
    from_email: str
    to_email: str
    subject: str
    body: str
    timestamp: datetime

class EmailAnalysis(BaseModel):
    phishing_detected: bool
    explanation: Optional[str] = None
    user_account_id: int

async def analyse_email(email: Email,account: str,db: Session = Depends(get_db)) -> EmailAnalysis:
    try:
        user_account_id = db.query(EmailAccountinDB).filter(EmailAccountinDB.email == account).first().id
        if not user_account_id:
            raise ValueError("User account not found")
        # Analyse the email for malware
        phishing_detected = False
        explanation = "No phishing detected"
        # See for whitelist
        whitelist = db.query(WhitelistInDb).filter(WhitelistInDb.email == email.from_email).first()
        if whitelist:
                return EmailAnalysis(phishing_detected=False, explanation="email is whitelisted", user_account_id=user_account_id)
        # See for blacklist
        blacklist = db.query(BlacklistInDb).filter(BlacklistInDb.email == email.from_email).first()
        if blacklist:
            return EmailAnalysis(phishing_detected=True, explanation="email is blacklisted", user_account_id=user_account_id)

        
        #Analyse PJ

        # Analyse the email for phishing
        async with httpx.AsyncClient() as client:
            response = await client.post("https://localhost:8080/IA", json={
                "email": email.dict()
            })
            phishing_detected = response.json().get("phishing_detected")
            explanation = response.json().get("explanation")
        return EmailAnalysis(phishing_detected=phishing_detected, explanation=explanation, user_account_id=user_account_id)


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))