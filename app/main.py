from fastapi import FastAPI, HTTPException
from loguru import logger
from pathlib import Path
import json

# --------------------------------------------------
# Configuration Loguru
# --------------------------------------------------
LOG_PATH = Path("logs/api.log")
LOG_PATH.parent.mkdir(exist_ok=True, parents=True)

logger.add(LOG_PATH, rotation="1 MB", encoding="utf-8", enqueue=True)
logger.info("🚀 Lancement de l'API DSN Checker")

# --------------------------------------------------
# Initialisation de FastAPI
# --------------------------------------------------
app = FastAPI(
    title="DSN Checker API",
    version="1.0.0",
    description="API permettant de vérifier et rechercher des rubriques DSN extraites du cahier technique."
)

# --------------------------------------------------
# Chargement des données JSON
# --------------------------------------------------
DATA_PATH = Path("data/rubriques.json")

if not DATA_PATH.exists():
    logger.error(f"❌ Fichier introuvable : {DATA_PATH.resolve()}")
    raise FileNotFoundError(f"Le fichier {DATA_PATH} est introuvable. Exécute d'abord le script d'extraction.")

try:
    logger.info(f"📂 Lecture du fichier {DATA_PATH}")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        dsn_data = json.load(f)
    logger.success(f"✅ {len(dsn_data)} rubriques chargées depuis {DATA_PATH.name}")
except Exception as e:
    logger.exception("💥 Erreur lors du chargement du fichier JSON")
    raise e

# Création d’un index par code pour recherche rapide
dsn_dict = {item["code"]: item for item in dsn_data}
logger.info(f"📇 Index des rubriques créé ({len(dsn_dict)} entrées)")

# --------------------------------------------------
# Routes API
# --------------------------------------------------
@app.get("/")
def root():
    logger.debug("Requête GET /")
    return {"message": "API DSN prête 🎯 — essayez /check/S10.G00.00.001"}


@app.get("/check/{code}")
def check_code(code: str):
    """
    Vérifie si un code DSN existe et retourne ses informations.
    """
    logger.info(f"🔎 Vérification du code DSN : {code}")
    item = dsn_dict.get(code)
    if not item:
        logger.warning(f"❌ Code non trouvé : {code}")
        raise HTTPException(status_code=404, detail="Code non trouvé dans les rubriques DSN")
    logger.success(f"✅ Code trouvé : {code}")
    return {"found": True, "data": item}


@app.get("/count")
def count_rubriques():
    """
    Retourne le nombre total de rubriques chargées.
    """
    logger.debug("Requête GET /count")
    return {"count": len(dsn_data)}
