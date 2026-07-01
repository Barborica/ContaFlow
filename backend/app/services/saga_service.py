import xml.etree.ElementTree as ET
from datetime import datetime

from app.models.document import Document


def generate_saga_xml(documents: list[Document]) -> str:
    """
    Generează un șir de caractere XML valid, gata de importat în SAGA C.I.S.
    pe baza documentelor aprobate.
    """
    # Rădăcina documentului XML solicitat de SAGA
    root = ET.Element("import")
    intrari = ET.SubElement(root, "intrari")

    for doc in documents:
        # SAGA are nevoie de datele furnizorului asociat
        vendor_name = doc.vendor.name if doc.vendor else "Furnizor Necunoscut"
        vendor_cui = doc.vendor.cui if doc.vendor else ""

        # Formătăm data în standardul românesc DD.MM.YYYY dacă este posibil
        try:
            # Încercăm să convertim dacă avem formatul din baza de date
            date_obj = datetime.strptime(str(doc.created_at), "%Y-%m-%d %H:%M:%S.%f")
            date_str = date_obj.strftime("%d.%m.%Y")
        except Exception:
            date_str = datetime.now().strftime("%d.%m.%Y")

        # 1. Secțiunea ANTET (Datele generale ale bonului/facturii)
        antet = ET.SubElement(intrari, "antet")

        # Tipul: 'B' pentru Bon Fiscal, gol pentru Factură
        ET.SubElement(antet, "tip").text = (
            "B" if str(doc.doc_type) == "BON_FISCAL" else ""
        )
        ET.SubElement(antet, "numar").text = f"CF-{doc.id}"
        ET.SubElement(antet, "data").text = date_str
        ET.SubElement(antet, "cod_furnizor").text = vendor_cui
        ET.SubElement(antet, "numitor_furnizor").text = vendor_name
        ET.SubElement(antet, "cui_furnizor").text = vendor_cui

        # Calcule contabile automate din Suma Totală (TVA 19% ca fallback standard)
        total = float(doc.total) if doc.total else 0.0  # type: ignore
        valoare_fara_tva = round(total / 1.21, 2)
        valoare_tva = round(total - valoare_fara_tva, 2)

        ET.SubElement(antet, "valoare").text = str(valoare_fara_tva)
        ET.SubElement(antet, "tva").text = str(valoare_tva)
        ET.SubElement(antet, "total").text = str(total)

        # 2. Secțiunea DETALII (Liniile din bon/articolul contabil)
        detalii = ET.SubElement(antet, "detalii")
        articol = ET.SubElement(detalii, "articol")

        ET.SubElement(articol, "denumire").text = "Cheltuieli nestocate (cf. OCR)"
        ET.SubElement(articol, "um").text = "BUC"
        ET.SubElement(articol, "cantitate").text = "1"
        ET.SubElement(articol, "pret").text = str(valoare_fara_tva)
        ET.SubElement(articol, "valoare").text = str(valoare_fara_tva)
        ET.SubElement(articol, "procent_tva").text = "21"
        ET.SubElement(articol, "tva").text = str(valoare_tva)

    xml_string = ET.tostring(root, encoding="utf-8", method="xml")
    return "\n" + xml_string.decode("utf-8")
