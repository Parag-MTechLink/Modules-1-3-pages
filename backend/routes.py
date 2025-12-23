from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
from backend.database import SessionLocal, engine
from backend.models import Base
from backend.services import EUTSchemaManager
import json
from sqlalchemy import text

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
# CREATE EUT
# --------------------------------
@router.post("/api/eut")
def add_or_update_eut(eut: dict, db: Session = Depends(get_db)):

    # 🔹 PAGE 1 → CREATE
    if not eut.get("product_id"):
        eut["product_id"] = f"EUT-{uuid.uuid4().hex[:8].upper()}"
        mode = "INSERT"
    else:
        mode = "UPDATE"

    schema_manager = EUTSchemaManager(
        engine=db.get_bind(),
        table_name="eut_details"
    )
    schema_manager.ensure_columns_from_payload(eut)

    # Convert dict/list → JSON
    for k, v in eut.items():
        if isinstance(v, (dict, list)):
            eut[k] = json.dumps(v)

    if mode == "INSERT":
        columns = ", ".join(f'"{k}"' for k in eut.keys())
        values = ", ".join(f":{k}" for k in eut.keys())

        sql = text(f"""
            INSERT INTO eut_details ({columns})
            VALUES ({values})
        """)
        db.execute(sql, eut)

    else:
        set_clause = ", ".join(
            f'"{k}" = :{k}' for k in eut.keys() if k != "product_id"
        )

        sql = text(f"""
            UPDATE eut_details
            SET {set_clause}
            WHERE product_id = :product_id
        """)
        result = db.execute(sql, eut)

        if result.rowcount == 0:
            raise HTTPException(
                status_code=400,
                detail="Update failed: product_id not found"
            )

    db.commit()

    return {
        "status": "success",
        "product_id": eut["product_id"]
    }




# --------------------------------
# READ ALL EUTs
# --------------------------------
@router.get("/api/eut")
def get_all_euts(db: Session = Depends(get_db)):
    """
    Return all EUTs as dictionaries.
    Required for dynamic schemas.
    """
    result = db.execute(text("SELECT * FROM eut_details"))
    return result.mappings().all()

# --------------------------------
# READ SINGLE EUT BY PRODUCT ID
# --------------------------------
@router.get("/api/eut/by-product/{product_id}")
def get_eut_by_product_id(product_id: str, db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM eut_details WHERE product_id = :pid"),
        {"pid": product_id}
    ).mappings().first()

    if not result:
        raise HTTPException(status_code=404, detail="EUT not found")

    return result

# --------------------------------
# READ SINGLE EUT
# --------------------------------
@router.get("/api/eut/{eut_id}")
def get_eut_by_id(eut_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM eut_details WHERE id = :id"),
        {"id": eut_id}
    ).mappings().first()

    if not result:
        raise HTTPException(status_code=404, detail="EUT not found")

    return result

# --------------------------------
# HOME ROUTE
# --------------------------------
@router.get("/", tags=["UI"])
def home():
    return RedirectResponse(url="/static/home.html")
