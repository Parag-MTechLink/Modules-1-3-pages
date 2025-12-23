from sqlalchemy import Column, Integer, String
from backend.database import Base
import uuid

class EUT(Base):
    __tablename__ = "eut_details"

    id = Column(Integer, primary_key=True, index=True)

    # Auto-generated, unique product ID
    product_id = Column(
        String,
        unique=True,
        index=True,
        default=lambda: f"EUT-{uuid.uuid4().hex[:8].upper()}"
    )

    name_of_eut = Column(String, nullable=False)

    quantity_of_eut = Column(Integer)

    manufacturer_address = Column(String)
