from fastapi import Depends, HTTPException
from db.models import BlacklistInDb
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from utils.users import UserInfo
from routers.auth import get_current_user

def add_to_main_blacklist(
    email_to_send: str,
    reason_to_send: str,
    db: Session,
    user: UserInfo = Depends(get_current_user)  # Ajout de la dépendance
):
    try:
        if not db:
            raise HTTPException(status_code=500, detail="La session de base de données est invalide.")

        # Créer une nouvelle entrée dans la blacklist
        new_entry = BlacklistInDb(
            email=email_to_send,
            reason=reason_to_send,
            main_blacklist=True,
            user_email=""
        )
        db.add(new_entry)
        db.commit()
        return {"message": "Email ajouté à la blacklist"}
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Erreur SQLAlchemy : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de base de données. Veuillez réessayer plus tard.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Une erreur inattendue est survenue. Veuillez réessayer.")
