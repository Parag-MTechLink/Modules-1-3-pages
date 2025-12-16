from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from backend.database import SessionLocal, engine
from backend.models import Base, EUT

# --------------------------------
# DB INIT
# --------------------------------
Base.metadata.create_all(bind=engine)

# --------------------------------
# ROUTER
# --------------------------------
router = APIRouter(tags=["EUT"])

# --------------------------------
# DB Dependency
# --------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------
# Pydantic Schemas
# --------------------------------
class EUTCreate(BaseModel):
    name: str
    quantity: int
    manufacturer_address: str
    model_number: str
    serial_number: str


class EUTResponse(EUTCreate):
    id: int

    class Config:
        orm_mode = True

# --------------------------------
# API ROUTES
# --------------------------------
@router.post("/api/eut", response_model=EUTResponse)
def add_eut(eut: EUTCreate, db: Session = Depends(get_db)):
    new_eut = EUT(**eut.dict())
    db.add(new_eut)
    db.commit()
    db.refresh(new_eut)
    return new_eut


@router.get("/api/eut", response_model=List[EUTResponse])
def get_all_euts(db: Session = Depends(get_db)):
    return db.query(EUT).all()


@router.get("/api/eut/{eut_id}", response_model=EUTResponse)
def get_eut_by_id(eut_id: int, db: Session = Depends(get_db)):
    eut = db.query(EUT).filter(EUT.id == eut_id).first()
    if not eut:
        raise HTTPException(status_code=404, detail="EUT not found")
    return eut

# --------------------------------
# HOME ROUTE (UI ENTRY)
# --------------------------------
@router.get("/", tags=["UI"])
def home():
    """
    Redirect to static frontend home.html
    """
    return RedirectResponse(url="/static/home.html")
