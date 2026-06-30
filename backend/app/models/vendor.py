from app.core.database import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    cui = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    address = Column(String, nullable=True)

    # func.now() lasă baza de date să genereze automat data și ora creării
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relația către documente (1 furnizor -> N documente)
    documents = relationship("Document", back_populates="vendor")
