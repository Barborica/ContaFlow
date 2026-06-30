from app.services.ocr_service import extract_text_from_image

rezultat = extract_text_from_image("uploads/test.jpg")
print("\n--- REZULTAT OCR ---")
print(rezultat)
print("--------------------")
