from app.services.anaf_service import get_company_details

cui_test = "42864258"

rezultat = get_company_details(cui_test)
print("\n--- REZULTAT API ALTERNATIV ---")
print(rezultat)
print("-------------------------------\n")
