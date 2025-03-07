from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from db.db import Base

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