
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os


DATABASE_URL = DATABASE_URL = os.getenv("DATABASE_URL") or "mysql+aiomysql://hookadmin:admin123@localhost:3306/Hookshield"

async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
