import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.models.document import Document
from app.services.ocr_service import extract_text_from_image

router = APIRouter()

os.makedirs("uploads", exist_ok=True)


def process_document_background(document_id: int, file_path: str):
    db = SessionLocal()
    try:
        extracted_text = extract_text_from_image(file_path)

        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            # --- MODIFICAT: Îi spunem lui Pylance să ignore avertismentul static ---
            doc.raw_text = extracted_text  # type: ignore
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
    # --- MODIFICAT: Tratam cazul în care filename vine gol (None) ---
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

    # --- MODIFICAT: Îi spunem lui Pylance să ignore tipul lui new_doc.id ---
    background_tasks.add_task(process_document_background, new_doc.id, file_location)  # type: ignore

    return {
        "document_id": new_doc.id,  # type: ignore
        "message": "Document încărcat cu succes. Procesare OCR inițiată în fundal.",
    }
