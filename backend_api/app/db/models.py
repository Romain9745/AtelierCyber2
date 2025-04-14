from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from db.db import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, func, CheckConstraint, UniqueConstraint, BigInteger, Enum
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
    blacklists = relationship("BlacklistInDb", back_populates="user")

class EmailAccountTypeinDB(Base):
    __tablename__ = 'email_account_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(Enum('imap', 'Google', name='email_account_type_enum'), nullable=False)

class EmailAccountinDB(Base):
    __tablename__ = 'email_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    added_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_type = Column(Integer, ForeignKey('email_account_types.id'), nullable=False)
    imap_password = Column(String(255))
    imap_host = Column(String(255))
    token = Column(String(255))
    created_at = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')

    # Relationships (if you want to access user and account type from EmailAccount)
    added_by_user = relationship('UserInDB', backref='email_accounts', passive_deletes=True)
    account_type_obj = relationship('EmailAccountTypeinDB', backref='email_accounts', passive_deletes=True)

class UserRole(Base):
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False)
    
class BlacklistInDb(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String(255), ForeignKey('users.email', ondelete="CASCADE"), nullable=False)
    email = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    added_at = Column(DateTime, default=func.now())
    main_blacklist = Column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name='chk_email_format'),
        UniqueConstraint('user_email', 'email', name='uix_user_email_email'),
    )

    user = relationship("UserInDB", back_populates="blacklists")
    
class WhitelistInDb(Base):
    __tablename__ = 'whitelist'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100))
    reason = Column(String(100))
    added_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name='chk_email_format'),
    )

class EmailFolderTypeinDB(Base):
    __tablename__ = 'email_folders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    folder_type = Column(Enum('HOOKSHIELD_SPAM','INBOX', name='email_folder_type_enum'), nullable=False)
    
    
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
    ticket = relationship('TicketInDB', backref='email_analyses')
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
    
class TicketInDB(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mail_uid = Column(Integer, ForeignKey('email_analyses.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_explanation = Column(Text, nullable=False)
    state = Column(Integer, default=1)
    made_at = Column(TIMESTAMP, server_default=func.now())
    last_modification_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship('UserInDB', backref='tickets')
    mail = relationship('MailsInDb', backref='tickets')