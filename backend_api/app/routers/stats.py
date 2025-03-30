from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from utils.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import GlobalStatsinDB, UserStatsinDB, MailsInDb, ReportinDB, FileSignatureinDB
from utils.users import  UserInDB
from routers.auth import get_current_user,CheckRole,Role, UserInfo

class GlobalStats(BaseModel):
    id: int
    total_users: int
    total_mail_analyzed: int
    total_mail_authentic: int
    total_mails_blocked: int
    total_files_scanned: int
    total_false_positive: int
    total_false_negative: int
    last_updated: datetime

class UserStats(BaseModel):
    id: int
    user_id: int
    total_reports: int
    mail_analyzed: int
    mail_authentic: int
    mail_blocked: int
    last_action: datetime

class MailStats(BaseModel):
    total_emails: int
    total_mails_blocked: int
    total_mail_authentic: int

class ReportStats(BaseModel):
    total_false_positive: int
    total_false_negative: int

class FileStats(BaseModel):
    total_files_scanned: int
    total_malware_detected: int

class StatsResponse(BaseModel):
    global_stats: GlobalStats
    email_stats: MailStats
    report_stats: ReportStats
    file_stats: FileStats


router = APIRouter(tags=["Stats"])

def fetch_stats_for_me(current_user: UserInfo, db) -> UserStats:
    # Query the user stats for the current user
    user_id = db.query(UserInDB).filter(UserInDB.email == current_user.email).first().id
    if not user_id:
        raise ValueError("User not found")
    user_stats = db.query(UserStatsinDB).filter(UserStatsinDB.user_id == user_id).first()
    if not user_stats:
        raise ValueError("User stats not found")

    # Return the stats in the required format
    return UserStats(
        id=user_stats.id,
        user_id=user_stats.user_id,
        total_reports=user_stats.total_reports,
        mail_analyzed=user_stats.mail_analyzed,
        mail_authentic=user_stats.mail_authentic,
        mail_blocked=user_stats.mails_blocked,
        last_action=user_stats.last_action
    )


def fetch_stats(db) -> StatsResponse:
    # Query the global stats (assuming only one record in the table)
    global_stats = db.query(GlobalStatsinDB).first()
    if not global_stats:
        raise ValueError("Global stats not found")

    # Email stats: Using SQLAlchemy functions to count and sum
    email_stats = db.query(
        func.count(MailsInDb.id).label("total_emails"),
        func.sum(MailsInDb.is_phishing).label("total_mails_blocked"),
        func.sum((~MailsInDb.is_phishing)).label("total_mail_authentic")
    ).first()

    email_stats_dict = {
        "total_emails": email_stats.total_emails or 0,
        "total_mails_blocked": email_stats.total_mails_blocked or 0,
        "total_mail_authentic": email_stats.total_mail_authentic or 0
    }

    # Report stats: Calculate false positives and false negatives
    report_stats = db.query(
        func.sum((ReportinDB.report_type == 'false_positive')).label("total_false_positive"),
        func.sum((ReportinDB.report_type == 'false_negative')).label("total_false_negative")
    ).first()

    report_stats_dict = {
        "total_false_positive": report_stats.total_false_positive or 0,
        "total_false_negative": report_stats.total_false_negative or 0
    }

    # File stats: Count files scanned and sum malware detections
    file_stats = db.query(
        func.count(FileSignatureinDB.id).label("total_files_scanned"),
        func.sum(FileSignatureinDB.detected_malware).label("total_malware_detected")
    ).first()

    file_stats_dict = {
        "total_files_scanned": file_stats.total_files_scanned or 0,
        "total_malware_detected": file_stats.total_malware_detected or 0
    }

    # Return the stats in the required format
    return StatsResponse(
        global_stats=GlobalStats(
            id=global_stats.id,
            total_users=global_stats.total_users,
            total_mail_analyzed=global_stats.total_mail_analyzed,
            total_mail_authentic=global_stats.total_mail_authentic,
            total_mails_blocked=global_stats.total_mails_blocked,
            total_files_scanned=global_stats.total_files_scanned,
            total_false_positive=global_stats.total_false_positive,
            total_false_negative=global_stats.total_false_negative,
            last_updated=global_stats.last_updated
        ),
        email_stats=MailStats(**email_stats_dict),
        report_stats=ReportStats(**report_stats_dict),
        file_stats=FileStats(**file_stats_dict)
    )

def get_user_stats(user_email: str, db) -> UserStats:
    # Query the user stats for the given user email
    user_id = db.query(UserInDB).filter(UserInDB.email == user_email).first().id
    user_stats = db.query(UserStatsinDB).filter(UserStatsinDB.user_id == user_id).first()
    if not user_stats:
        raise ValueError("User stats not found")

    # Return the stats in the required format
    return UserStats(
        id=user_stats.id,
        user_id=user_stats.user_id,
        total_reports=user_stats.total_reports,
        mail_analyzed=user_stats.mail_analyzed,
        mail_authentic=user_stats.mail_authentic,
        mail_blocked=user_stats.mails_blocked,
        last_action=user_stats.last_action
    )

# Route to get all stats
@router.get("/stats", response_model=StatsResponse, dependencies=[Depends(CheckRole(Role.admin))])
def get_stats(db: Session = Depends(get_db)):
    try: 
        return fetch_stats(db)
    except Exception as e:
        print(e)
        return {"message": "Error fetching stats"}


# Route to get stats for a specific user
@router.get("/stats/me", response_model=UserStats)
def get_my_stats(current_user: UserInfo = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return fetch_stats_for_me(current_user, db)
    except Exception as e:
        print(e)
        return {"message": "Error fetching stats"}

@router.get("/stats/user/{user_email}", response_model=UserStats, dependencies=[Depends(CheckRole(Role.admin))])
def get_user_stats_route(user_email: str, db: Session = Depends(get_db)):
    try:
        return get_user_stats(user_email, db)
    except Exception as e:
        print(e)
        return {"message": "Error fetching stats"}
    

def create_global_stats(db: Session):
    try:
        if db.query(GlobalStatsinDB).count() > 0:
            return {"message": "Global stats already exist"}
        new_global_stats = GlobalStatsinDB()
        db.add(new_global_stats)
        db.commit()
        return {"message": "Global stats created"}
    except Exception as e:
        print(e)
        return {"message": "Error creating global stats"}
