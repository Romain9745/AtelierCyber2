
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select




async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()