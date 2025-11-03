import csv
import json
from loguru import logger

from ingest import (
    get_location_from_yaml,
    download_pdf, read_pdf_from_page, clean_pdf_text
)
from parse import detect_rubriques

YEAR = "2025"

config = get_location_from_yaml().get("cahier-technique").get(YEAR)

# Example usage
download_pdf(
    url=config.get("url"),
    filename=f"data/cahier_{YEAR}.pdf",
)

logger.success("PDF téléchargé !")
logger.info("Processing PDF")

# Example usage
pdf_text = read_pdf_from_page(f"data/cahier_{YEAR}.pdf", start_page=config.get('start'))

logger.info("Nettoyage du PDF")

cleaned_text = clean_pdf_text(pdf_text)

logger.info("Extraction des rubriques")

results = detect_rubriques(cleaned_text)

logger.success("Sauvegarde intermédiaire")

# Sauvegarde au format JSON
with open("data/rubriques.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

