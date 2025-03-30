from datetime import datetime
from pydantic import BaseModel
import httpx
from db.models import WhitelistInDb, BlacklistInDb,EmailAccountinDB
from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from utils.pièce_jointe import *



class Email(BaseModel):
    email_id: int
    from_email: str
    to_email: str
    subject: str
    body: str
    timestamp: datetime
    attachments: list[dict]

class EmailAnalysis(BaseModel):
    phishing_detected: bool
    explanation: Optional[str] = None
    user_account_id: int

async def analyse_email(email: Email,account: str,db: Session) -> EmailAnalysis:
    try:
        user_account= db.query(EmailAccountinDB).filter(EmailAccountinDB.email == account).first()
        user_account_id = user_account.id

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
        GlobalBlacklist = db.query(BlacklistInDb).filter(BlacklistInDb.email == email.from_email,BlacklistInDb.main_blacklist == True).first()
        UserBlacklist = db.query(BlacklistInDb).filter(BlacklistInDb.email == email.from_email,BlacklistInDb.user_email == user_account.email).first()
        if GlobalBlacklist or UserBlacklist:
            return EmailAnalysis(phishing_detected=True, explanation="email is blacklisted", user_account_id=user_account_id)

        
        #Analyse PJ
        for attachment in email.attachments:
            file_path = f"/tmp/{attachment['filename']}"
            with open(file_path, 'wb') as f:
                f.write(attachment['data'])
            analysis_id = await upload_file(file_path)
            if analysis_id:
                report = await get_report(analysis_id)
                if any(result.get('category') == 'malicious' for result in report.values()):
                    phishing_detected = True
                    explanation = f"Malicious attachment detected: {attachment['filename']}"
                    break
        
        # Analyse the email for phishing
        async with httpx.AsyncClient() as client:
            response = await client.post("https://localhost:8080/IA", json={
            "email": {**email.dict(), "timestamp": email.timestamp.isoformat()}
            })
            phishing_detected = response.json().get("phishing_detected")
            explanation = response.json().get("explanation")        
        return EmailAnalysis(phishing_detected=phishing_detected, explanation=explanation, user_account_id=user_account_id)


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))