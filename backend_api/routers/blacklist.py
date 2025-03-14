from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.db import SessionLocal
from db.models import BlacklistInDb, WhitelistInDb

router = APIRouter(tags=["Blacklist"])

class ListInfo(BaseModel):
    email: str
    reason: str
    user_email: str
    
class ListInfoToSend(BaseModel):
    email: str
    reason: str
    
class UserEmail(BaseModel):
    email: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@router.get('/main_blacklist')
def get_main_blacklist(db: Session = Depends(get_db)):
    try:
        results = db.query(BlacklistInDb.email, BlacklistInDb.reason).filter(BlacklistInDb.main_blacklist == True).all()
        if results:
            return [ListInfoToSend(email=result.email, reason=result.reason) for result in results]
        else:
            raise HTTPException(status_code=404, detail="No blacklist entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/get_user_blacklist')
def get_main_blacklist(entry: UserEmail, db: Session = Depends(get_db)):
    try:
        results = db.query(BlacklistInDb.email, BlacklistInDb.reason, BlacklistInDb.user_email).filter(and_(BlacklistInDb.user_email==entry.email, BlacklistInDb.main_blacklist == False)).all()
        if results:
            for result in results:
                print("user mail = "+result.user_email) 
            return [ListInfoToSend(email=result.email, reason=result.reason) for result in results]
        else:
            return {"message": "No blacklist entries found for this user."}    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/whitelist')
def get_whitelist(db: Session = Depends(get_db)):
    try:
        results = db.query(WhitelistInDb.email, WhitelistInDb.reason).all()
        if results:
            return [ListInfoToSend(email=result.email, reason=result.reason) for result in results]
        else:
            raise HTTPException(status_code=404, detail="No whitelist entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/main_blacklist')
def add_to_main_blacklist(entry: ListInfo, db: Session = Depends(get_db)):
    try:
        new_entry = BlacklistInDb(email=entry.email, reason=entry.reason, main_blacklist=True, user_email=entry.user_email)
        db.add(new_entry)
        db.commit()
        return {"message": "Email ajouté à la blacklist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/user_blacklist')
def add_to_user_blacklist(entry: ListInfo, db: Session = Depends(get_db)):
    print(entry);
    try:
        new_entry = BlacklistInDb(email=entry.email, reason=entry.reason, main_blacklist=False, user_email=entry.user_email)
        db.add(new_entry)
        db.commit()
        return {"message": "Email ajouté à la blacklist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/whitelist')
def add_to_whitelist(entry: ListInfo, db: Session = Depends(get_db)):
    try:
        new_entry = WhitelistInDb(email=entry.email, reason=entry.reason)
        db.add(new_entry)
        db.commit()
        return {"message": "Email ajouté à la whitelist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete('/blacklist')
def delete_from_blacklist(email: str, db: Session = Depends(get_db)):
    try:
        entry = db.query(BlacklistInDb).filter(BlacklistInDb.email == email).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Email non trouvé dans la blacklist")
        
        db.delete(entry)
        db.commit()
        return {"message": "Email supprimé de la blacklist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/whitelist')
def delete_from_whitelist(email: str, db: Session = Depends(get_db)):
    try:
        entry = db.query(WhitelistInDb).filter(WhitelistInDb.email == email).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Email non trouvé dans la whitelist")
        
        db.delete(entry)
        db.commit()
        return {"message": "Email supprimé de la whitelist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
