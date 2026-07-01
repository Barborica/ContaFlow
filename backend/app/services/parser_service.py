import logging
import re

logger = logging.getLogger(__name__)


def parse_document_text(raw_text: str) -> dict:
    """
    Analizează textul brut extras de OCR și caută tipare (Regex) pentru CUI, Dată și Total.
    Returnează un dicționar cu datele curățate.
    """
    data: dict[str, str | None] = {"cui": None, "date": None, "total": None}

    if not raw_text:
        return data

    # 1. Extragere CUI
    # Explicatie Regex: Caută opțional cuvintele CIF/CUI/RO, permite spații,
    # caută din nou opțional RO, și capturează exact 6 până la 10 cifre.
    cui_pattern = r"(?:CIF|CUI|RO|C\.I\.F\.)?\s*(?:RO)?\s*([0-9]{6,10})"
    cui_match = re.search(cui_pattern, raw_text, re.IGNORECASE)
    if cui_match:
        data["cui"] = cui_match.group(1)

    # 2. Extragere Dată
    # Explicatie Regex: Caută 2 cifre, urmate de . / sau -, apoi 2 cifre, apoi 4 cifre
    date_pattern = r"(\d{2}[\./-]\d{2}[\./-]\d{4})"
    date_match = re.search(date_pattern, raw_text)
    if date_match:
        data["date"] = date_match.group(1)

    # 3. Extragere Sumă Totală
    # Explicatie Regex: Caută cuvântul TOTAL, permite orice caractere (inclusiv pe linii noi),
    # și capturează un număr care se termină cu două zecimale (ex: 10.00 sau 10,00)
    total_pattern = r"TOTAL.*?(?:LEI)?.*?(\d+[\.,]\d{2})"
    total_match = re.search(total_pattern, raw_text, re.IGNORECASE | re.DOTALL)
    if total_match:
        # Înlocuim posibila virgulă cu punct pentru standardizare în baza de date
        data["total"] = total_match.group(1).replace(",", ".")

    logger.info(f"Parsare finalizată. Date găsite: {data}")
    return data
