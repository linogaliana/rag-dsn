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
# Chargement des données
# --------------------------------------------------
DATA_PATH = Path("data/rubriques.json")

if not DATA_PATH.exists():
    logger.error(f"❌ Fichier introuvable : {DATA_PATH.resolve()}")
    raise FileNotFoundError(f"Le fichier {DATA_PATH} est introuvable. Exécute d'abord le script d'extraction.")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    dsn_data = json.load(f)
logger.success(f"✅ {len(dsn_data)} rubriques chargées depuis {DATA_PATH.name}")

dsn_dict = {item["code"]: item for item in dsn_data}
logger.info(f"📇 Index des rubriques créé ({len(dsn_dict)} entrées)")

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.get("/")
def root():
    logger.debug("GET /")
    return {"message": "API DSN prête 🎯 — essayez /check/S10.G00.00.001 ou /liste_rubriques"}


@app.get("/check/{code}")
def check_code(code: str):
    logger.info(f"🔎 Vérification du code DSN : {code}")
    item = dsn_dict.get(code)
    if not item:
        logger.warning(f"❌ Code non trouvé : {code}")
        raise HTTPException(status_code=404, detail="Code non trouvé dans les rubriques DSN")
    logger.success(f"✅ Code trouvé : {code}")
    return {"found": True, "data": item}


@app.get("/count")
def count_rubriques():
    logger.debug("GET /count")
    return {"count": len(dsn_data)}


@app.get("/liste_rubriques")
def liste_rubriques():
    """
    Retourne la liste complète des rubriques DSN.
    ⚠️ Attention : peut être volumineux !
    """
    logger.info("📤 Envoi de la liste des codes DSN uniquement")
    codes = list(dsn_dict.keys())
    return {"count": len(codes), "codes": codes}
