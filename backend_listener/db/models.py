from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

Base = declarative_base()

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
    