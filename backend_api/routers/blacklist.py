from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.db import SessionLocal
from db.models import BlacklistInDb, WhitelistInDb, UserBlacklistInDb

router = APIRouter()

class ListInfo(BaseModel):
    email: str
    reason: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@router.get('/main_blacklist')
def get_main_blacklist(db: Session = Depends(get_db)):
    try:
        results = db.query(BlacklistInDb.email, BlacklistInDb.reason).all()
        if results:
            return [ListInfo(email=result.email, reason=result.reason) for result in results]
        else:
            raise HTTPException(status_code=404, detail="No blacklist entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/whitelist')
def get_whitelist(db: Session = Depends(get_db)):
    try:
        results = db.query(WhitelistInDb.email, WhitelistInDb.reason).all()
        if results:
            return [ListInfo(email=result.email, reason=result.reason) for result in results]
        else:
            raise HTTPException(status_code=404, detail="No whitelist entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/user_blacklist')
def get_user_blacklist(db: Session = Depends(get_db)):
    try:
        results = db.query(UserBlacklistInDb.email, UserBlacklistInDb.reason).all()
        if results:
            return [ListInfo(email=result.email, reason=result.reason) for result in results]
        else:
            raise HTTPException(status_code=404, detail="No blacklist entry found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/main_blacklist')
def add_to_main_blacklist(entry: ListInfo, db: Session = Depends(get_db)):
    try:
        new_entry = BlacklistInDb(email=entry.email, reason=entry.reason)
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
    
@router.post('/user_blacklist')
def add_to_blacklist(entry: ListInfo, db: Session = Depends(get_db)):
    try:
        new_entry = UserBlacklistInDb(email=entry.email, reason=entry.reason)
        db.add(new_entry)
        db.commit()
        return {"message": "Email ajouté à la blacklist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete('/main_blacklist')
def delete_from_blacklist(email: str, db: Session = Depends(get_db)):
    print("début suppression email")
    try:
        print("email reçu : "+email)
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
    
@router.delete('/user_blacklist')
def delete_from_user_blacklist(email: str, db: Session = Depends(get_db)):
    try:
        entry = db.query(UserBlacklistInDb).filter(UserBlacklistInDb.email == email).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Email non trouvé dans la blacklist")
        
        db.delete(entry)
        db.commit()
        return {"message": "Email supprimé de la whitelist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


