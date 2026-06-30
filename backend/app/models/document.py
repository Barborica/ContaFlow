from app.core.database import Base
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)

    doc_type = Column(String, nullable=False)  # 'FACTURA' sau 'BON_FISCAL'
    file_path = Column(String, nullable=False)
    doc_number = Column(String, nullable=True)
    doc_date = Column(Date, nullable=True)
    total = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    raw_text = Column(Text, nullable=True)
    status = Column(String, index=True, nullable=False, default="UPLOADED")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # onupdate=func.now() actualizează automat data când rândul este modificat
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relația inversă către furnizor
    vendor = relationship("Vendor", back_populates="documents")
