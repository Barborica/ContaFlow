import os
import shutil
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.models.document import Document
from app.models.vendor import Vendor  # Avem nevoie și de modelul de furnizor
from app.services.anaf_service import get_company_details
from app.services.ocr_service import extract_text_from_image
from app.services.parser_service import parse_document_text

router = APIRouter()

os.makedirs("uploads", exist_ok=True)


def process_document_background(document_id: int, file_path: str):
    db = SessionLocal()
    try:
        # 1. OCR
        extracted_text = extract_text_from_image(file_path)

        # 2. Regex Parser
        parsed_data = parse_document_text(extracted_text)

        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.raw_text = extracted_text  # type: ignore

        # Salvăm sumele și data găsite
        if parsed_data.get("total"):
            doc.total = float(parsed_data["total"])  # type: ignore

        # 3. Interogare API Firme (dacă am găsit CUI)
        if parsed_data.get("cui"):
            cui_found = parsed_data["cui"]
            company_data = get_company_details(cui_found)  # type: ignore

            if company_data:
                # Căutăm dacă furnizorul există deja în baza de date
                vendor = db.query(Vendor).filter(Vendor.cui == cui_found).first()

                # Dacă nu există, îl creăm
                if not vendor:
                    vendor = Vendor(
                        cui=cui_found,
                        name=company_data.get("name"),
                        address=company_data.get("address"),
                    )
                    db.add(vendor)
                    db.commit()
                    db.refresh(vendor)

                # Asociem documentul cu furnizorul găsit/creat
                doc.vendor_id = vendor.id  # type: ignore

        doc.status = "NEEDS_REVIEW"  # type: ignore
        db.commit()

    except Exception as e:
        print(f"Eroare în background task: {e}")
    finally:
        db.close()


@router.post("/upload", status_code=202)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: Session = Depends(get_db),
):
    safe_filename = file.filename or "document.jpg"
    file_extension = safe_filename.split(".")[-1]

    unique_filename = f"{uuid4()}.{file_extension}"
    file_location = f"uploads/{unique_filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = Document(doc_type=doc_type, file_path=file_location, status="UPLOADED")
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    background_tasks.add_task(process_document_background, new_doc.id, file_location)  # type: ignore

    return {
        "document_id": new_doc.id,  # type: ignore
        "message": "Document încărcat cu succes. Procesare OCR inițiată în fundal.",
    }


class DocumentUpdate(BaseModel):
    total: float
    status: str
    vendor_id: int | None = None


@router.get("/")
def get_documents(db: Session = Depends(get_db)):
    """Returnează lista tuturor documentelor pentru interfața de revizuire."""
    return db.query(Document).all()


@router.put("/{document_id}")
def update_document(
    document_id: int, update_data: DocumentUpdate, db: Session = Depends(get_db)
):
    """Permite aprobarea sau corectarea datelor OCR."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document negăsit")

    doc.total = update_data.total  # type: ignore
    doc.status = update_data.status  # type: ignore
    if update_data.vendor_id:
        doc.vendor_id = update_data.vendor_id  # type: ignore

    db.commit()
    return {"message": "Document actualizat cu succes"}
