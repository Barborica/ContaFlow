import logging

import requests

logger = logging.getLogger(__name__)


def get_company_details(cui: str) -> dict[str, str | bool]:
    """
    Interoghează API-ul lista-firme.info și formatează datele pentru baza noastră de date.
    """
    if not cui:
        return {}

    clean_cui = "".join(filter(str.isdigit, cui))
    if not clean_cui:
        return {}

    url = f"https://lista-firme.info/api/v1/info?cui={clean_cui}"

    try:
        logger.info(f"Interogăm API pentru CUI: {clean_cui}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 1. Extragem datele adresei
        addr_info = data.get("address", {})
        street = addr_info.get("street", "")
        number = addr_info.get("number", "")
        city = addr_info.get("city", "")
        county = addr_info.get("county", "")

        # 2. Construim adresa frumos formatată
        address_parts = []
        if street:
            address_parts.append(f"Str. {street}")
        if number:
            address_parts.append(f"Nr. {number}")
        if city:
            address_parts.append(city)
        if county:
            address_parts.append(f"Jud. {county}")

        full_address = ", ".join(address_parts)

        # 3. Creăm dicționarul final
        extracted_info: dict[str, str | bool] = {
            "name": data.get("name", ""),
            "address": full_address,
            "tva_status": False,  # Acest API nu dă flag-ul de TVA, lăsăm False momentan
        }

        logger.info(f"Firmă identificată: {extracted_info['name']}")
        return extracted_info

    except Exception as e:
        logger.error(f"Eroare la comunicarea cu API-ul: {e}")
        return {}
