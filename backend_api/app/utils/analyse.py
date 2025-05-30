from datetime import datetime
from pydantic import BaseModel
import httpx
from db.models import WhitelistInDb, BlacklistInDb,EmailAccountinDB
from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from utils.pièce_jointe import *
from utils.add_to_blacklist import *
from db.models import UserInDB
API_KEY = "your-secure-api-key"
API_KEY_NAME = "X-API-KEY"

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
        user = db.query(UserInDB).filter(UserInDB.id == user_account.added_by).first()

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
        print(email.from_email)
        UserBlacklist = db.query(BlacklistInDb).filter(BlacklistInDb.email == email.from_email,BlacklistInDb.user_email == user.email).first()
        print(UserBlacklist,user_account.email)
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
        async with httpx.AsyncClient(timeout=httpx.Timeout(1000.0)) as client:
            try:
                response = await client.post(
                "http://host.docker.internal:7080/predict",
                json={"email_content": email.body},
                headers={API_KEY_NAME: API_KEY}  # Add the API key in the header
                )
            except httpx.RequestError as e:
                print(f"An error occurred while sending the request: {e}")
            phishing = response.json().get("label")
            if phishing == "phishing":
                phishing_detected = True
            else:
                phishing_detected = False
            explanation = response.json().get("explanation")
            if phishing_detected==True:
                add_to_main_blacklist(email.from_email, "Send a phishing email to "+email.to_email, db)
        return EmailAnalysis(phishing_detected=phishing_detected, explanation=explanation, user_account_id=user_account_id)


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))