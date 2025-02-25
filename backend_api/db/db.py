from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base


# Configuration de la connexion MariaDB
DATABASE_URL = "mysql+pymysql://hookadmin:admin123@localhost:3306/Hookshield"

# Connexion à la base de données
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()
