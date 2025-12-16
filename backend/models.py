from sqlalchemy import Column, Integer, String
from backend.database import Base

class EUT(Base):
    __tablename__ = "eut_details"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    manufacturer_address = Column(String)
    model_number = Column(String)
    serial_number = Column(String)
