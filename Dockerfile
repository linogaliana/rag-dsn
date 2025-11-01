# -----------------------------
# 🐍 1. Base image officielle Python
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# 🧰 2. Configuration du container
# -----------------------------
WORKDIR /app

# -----------------------------
# 📦 3. Installer les dépendances
# -----------------------------
COPY pyproject.toml .

RUN pip install uv && uv sync

# -----------------------------
# 📁 4. Copier le code de l'application
# -----------------------------
COPY app ./app
COPY src ./src


# -----------------------------
# 🚀 5. Commande de lancement
# -----------------------------
EXPOSE 8000

# Utilise "uv run uvicorn" si tu veux exploiter uv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
