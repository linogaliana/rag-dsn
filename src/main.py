import csv
import json
from loguru import logger

from src.ingest import download_pdf, read_pdf_from_page, clean_pdf_text
from src.parse import detect_rubriques

# Example usage
download_pdf(
    url="https://www.net-entreprises.fr/media/documentation/dsn-cahier-technique-2025.1.pdf",
    filename="data/cahier.pdf",
)

logger.success("PDF téléchargé !")
logger.info("Processing PDF")

# Example usage
pdf_text = read_pdf_from_page("data/cahier.pdf", start_page=126)

logger.info("Nettoyage du PDF")

cleaned_text = clean_pdf_text(pdf_text)

logger.info("Extraction des rubriques")

results = detect_rubriques(cleaned_text)

logger.success("Sauvegarde intermédiaire")

# Sauvegarde au format JSON
with open("data/rubriques.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)


fieldnames = list(results[0].keys())

with open("data/rubriques.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
