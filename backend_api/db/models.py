from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from db.db import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, func, CheckConstraint, BigInteger, Enum
from sqlalchemy.ext.declarative import declarative_base


class UserInDB(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('user_roles.id', ondelete='CASCADE'), nullable=False, default=2)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)

    role = relationship('UserRole', backref='users')

class UserRole(Base):
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False)
    
class BlacklistInDb(Base):
    __tablename__ = 'blacklist'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100))
    reason = Column(String(100))
    added_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name='chk_email_format'),
    )
    
class WhitelistInDb(Base):
    __tablename__ = 'whitelist'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100))
    reason = Column(String(100))
    added_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name='chk_email_format'),
    )
    
    
class UserBlacklistInDb(Base):
    __tablename__ = 'user_blacklist'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100))
    reason = Column(String(100))
    added_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name='chk_email_format'),
    )

class MailsInDb(Base):
    __tablename__ = 'email_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(255), nullable=False)
    recipient = Column(String(100), nullable=False)
    source = Column(String(100), nullable=False)
    receive_date = Column(DateTime, default=func.now())
    analyzed_date = Column(DateTime, default=func.now())
    email_body = Column(Text, nullable=False)
    is_phishing = Column(Boolean, nullable=False)
    blocked_date = Column(DateTime, nullable=True)
    explanation = Column(Text, nullable=False)
    folder_id = Column(Integer, ForeignKey('email_folders.id', ondelete='CASCADE'), nullable=False)

    source_email = Column(String, ForeignKey('email_accounts.email', ondelete='CASCADE'))
    __table_args__ = (
        CheckConstraint("recipient LIKE '%@%.%'", name='chk_recipient_email_format'),
        CheckConstraint("source LIKE '%@%.%'", name='chk_source_email_format'),
    )


class GlobalStatsinDB(Base):
    __tablename__ = "global_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_users = Column(BigInteger, default=0)
    total_mail_analyzed = Column(BigInteger, default=0)
    total_mail_authentic = Column(BigInteger, default=0)
    total_mails_blocked = Column(BigInteger, default=0)
    total_files_scanned = Column(BigInteger, default=0)
    total_false_positive = Column(BigInteger, default=0)
    total_false_negative = Column(BigInteger, default=0)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class UserStatsinDB(Base):
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_reports = Column(BigInteger, default=0)
    last_action = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    mail_analyzed = Column(BigInteger, default=0)
    mail_authentic = Column(BigInteger, default=0)
    mails_blocked = Column(BigInteger, default=0)

    user = relationship("UserInDB", backref="user_stats")

class ReportinDB(Base):
    __tablename__ = 'reporting'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email_id = Column(Integer, ForeignKey('email_analyses.id'), nullable=False)
    report_type = Column(Enum('false_positive', 'false_negative'), nullable=False)
    report_date = Column(DateTime, default=func.current_timestamp())

class FileSignatureinDB(Base):
    __tablename__ = 'file_signatures'
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    file_type = Column(String(50), nullable=False)
    detected_malware = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=func.current_timestamp())
    folder_id = Column(Integer, ForeignKey('email_folders.id', ondelete='CASCADE'), nullable=False)