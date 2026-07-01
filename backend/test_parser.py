from app.services.parser_service import parse_document_text

text_din_ocr = """
MRA&ETAEUROTRANSS.R.L.
STRADASTIINTEI,NUMARUL 1
CIFRO42864258
CURSA:1C2STOICANI-TULUCESTI
29.06.202608:41
TOTAL LEI
10.00
NUMERAR LEI
10.00
"""

rezultat = parse_document_text(text_din_ocr)
print("\n--- REZULTAT PARSARE ---")
print(f"CUI Găsit: {rezultat['cui']}")
print(f"Data Găsită: {rezultat['date']}")
print(f"Total Găsit: {rezultat['total']}")
print("------------------------\n")
