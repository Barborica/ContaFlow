import logging

from paddleocr import PaddleOCR

# Configurăm un sistem de log-uri pentru a vedea în terminal ce face serverul
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inițializăm modelul de AI în memorie la pornirea aplicației.
# use_angle_cls=True -> Ajută foarte mult dacă poza bonului e făcută puțin strâmb.
# lang='ro' -> Îi spune să recunoască și diacriticele specifice limbii române.
logger.info("Se încarcă modelul PaddleOCR...")
ocr_model = PaddleOCR(use_angle_cls=True, lang="ro")


def extract_text_from_image(file_path: str) -> str:
    """
    Primește calea către o imagine fizică de pe disc.
    Rulează algoritmul OCR și returnează tot textul găsit sub forma unui singur String,
    cu fiecare linie separată prin 'Enter' (\n).
    """
    logger.info(f"Începe procesarea OCR pentru imaginea: {file_path}")

    try:
        # cls=True activează clasificatorul de unghi
        result = ocr_model.ocr(file_path)

        extracted_lines = []

        # PaddleOCR returnează o listă destul de complexă:
        # [ [ [[x,y], [x,y]...], ('Textul găsit', confidenta_0_99) ], ... ]
        # Noi trebuie să extragem doar 'Textul găsit'.

        if result and result[0]:
            for line in result[0]:
                text = line[1][0]  # Extragem strict string-ul
                extracted_lines.append(text)

        # Unim toate liniile găsite într-un singur text mare
        full_text = "\n".join(extracted_lines)

        logger.info("Procesare OCR finalizată cu succes.")
        return full_text

    except Exception as e:
        logger.error(f"Eroare critică în timpul procesării OCR: {e}")
        return ""
