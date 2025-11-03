from pathlib import Path
import json
from loguru import logger

from ingest import (
    get_location_from_yaml,
    download_pdf, read_pdf_from_page, clean_pdf_text
)
from parse import detect_rubriques


def pipeline_prod_json(year: int | str, config: dict):
    """
    Pipeline complète :
    - récupère les infos de config YAML
    - télécharge le PDF correspondant
    - lit, nettoie et extrait les rubriques
    - sauvegarde le résultat en JSON
    """

    year = str(year)

    config = config.get("cahier-technique").get(year)
    if config is None:
        raise ValueError(f"Aucune configuration trouvée pour l'année {year} dans le YAML.")

    # Dossier de sortie
    Path("data").mkdir(parents=True, exist_ok=True)

    # Téléchargement du PDF
    download_pdf(
        url=config.get("url"),
        filename=f"data/cahier_{year}.pdf",
    )

    logger.success(f"PDF {year} téléchargé !")
    logger.info(f"Processing PDF {year}")

    # Lecture du texte PDF à partir de la page indiquée
    pdf_text = read_pdf_from_page(
        f"data/cahier_{year}.pdf",
        start_page=config.get("start")
    )

    logger.info(f"Nettoyage du PDF {year}")
    cleaned_text = clean_pdf_text(pdf_text)

    logger.info(f"Extraction des rubriques {year}")
    results = detect_rubriques(cleaned_text)

    logger.success(f"Sauvegarde intermédiaire {year}")

    # Sauvegarde JSON
    output_file = Path(f"data/rubriques_{year}.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.success(f"Résultat sauvegardé : {output_file.resolve()}")


config = get_location_from_yaml()

for years in list(range(2021, 2026)):
    pipeline_prod_json(years, config)