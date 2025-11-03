from fastapi import FastAPI, HTTPException, Query
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
    version="0.1.0",
    description="API permettant de vérifier et rechercher des rubriques DSN extraites du cahier technique, par année.",
)


# --------------------------------------------------
# Fonction utilitaire : chargement dynamique selon l’année
# --------------------------------------------------
def load_dsn_data(annee: int | str):
    """Charge les rubriques DSN pour une année donnée."""
    annee = str(annee)
    data_path = Path(f"data/rubriques_{annee}.json")

    if not data_path.exists():
        logger.error(f"❌ Fichier introuvable : {data_path.resolve()}")
        raise HTTPException(
            status_code=404,
            detail=f"Le fichier {data_path.name} est introuvable. Exécute d'abord le script d'extraction pour {annee}.",
        )

    with open(data_path, "r", encoding="utf-8") as f:
        dsn_data = json.load(f)

    logger.info(f"✅ {len(dsn_data)} rubriques chargées pour {annee}")
    dsn_dict = {item["code"]: item for item in dsn_data}
    return dsn_data, dsn_dict


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/")
def root():
    logger.debug("GET /")
    return {
        "message": "API DSN prête 🎯 — essayez /check/S10.G00.00.001?annee=2025 ou /liste_rubriques?annee=2024"
    }


@app.get("/check/{code}")
def check_code(code: str, annee: int = Query(..., description="Année du cahier technique")):
    logger.info(f"🔎 Vérification du code {code} pour {annee}")
    dsn_data, dsn_dict = load_dsn_data(annee)

    item = dsn_dict.get(code)
    if not item:
        logger.warning(f"❌ Code non trouvé : {code} ({annee})")
        raise HTTPException(status_code=404, detail=f"Code {code} non trouvé pour {annee}")

    logger.success(f"✅ Code trouvé : {code} ({annee})")
    return {"found": True, "annee": annee, "data": item}


@app.get("/count")
def count_rubriques(annee: int = Query(..., description="Année du cahier technique")):
    logger.debug(f"GET /count?annee={annee}")
    dsn_data, _ = load_dsn_data(annee)
    return {"annee": annee, "count": len(dsn_data)}


@app.get("/liste_rubriques")
def liste_rubriques(annee: int = Query(..., description="Année du cahier technique")):
    """Retourne la liste complète des rubriques DSN pour une année donnée."""
    logger.info(f"📤 Envoi de la liste des rubriques pour {annee}")
    _, dsn_dict = load_dsn_data(annee)
    codes = list(dsn_dict.keys())
    return {"annee": annee, "count": len(codes), "codes": codes}
