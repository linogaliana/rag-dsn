import re

import re

def detect_rubriques(text: str):
    """
    Détecte les rubriques (ligne avec code DSN Sxx.Gxx.xx.xxx en fin de ligne),
    récupère la ligne suivante (nom technique),
    et extrait la description entre cette rubrique et la suivante.

    Fonctionnalités :
    - Exclut toute ligne contenant CCH-<digits> ou SIG-<digits>
    - Associe à chaque rubrique le numéro de page à partir des marqueurs === [PAGE X] ===
    - Détecte les modalités (lignes du type 'dd - texte')
    - Insère un retour à la ligne avant chaque CCH/SIG
    - Extrait les blocs de contrôle (CCH/SIG) et les retire du champ 'description'
    - Supprime les marqueurs 'X [**,**]'
    """

    # --- 1️⃣ Séparer et nettoyer les lignes
    lines = [listing.strip() for listing in text.splitlines() if listing.strip()]

    regex_page = r"^=== \[PAGE (\d+)\] ===$"
    regex_rubrique = r"S\d{2}\.G\d{2}\.\d{2}\.\s*\d{3}$"

    rubriques = []
    current_page = None
    cleaned_lines = []

    # --- 2️⃣ Identifier les pages et nettoyer les lignes
    for line in lines:
        m = re.match(regex_page, line)
        if m:
            current_page = int(m.group(1))
            continue  # on ne garde pas le marqueur de page

        # 🔹 Ajout : saut de ligne avant CCH/SIG même avec espaces
        line = re.sub(r"\s*(?=(?:CCH|SIG)\s*-\s*\d+)", "\n", line)

        cleaned_lines.append((line.strip(), current_page))  # (texte, page)

    # --- 3️⃣ Localiser les rubriques
    for i, (line, page) in enumerate(cleaned_lines):
        if re.search(regex_rubrique, line):
            # exclure les lignes de contrôle pures
            if re.search(r"(?:CCH|SIG)\s*-\s*\d+", line):
                continue
            if i + 1 < len(cleaned_lines):
                next_line, _ = cleaned_lines[i + 1]
                rubriques.append((i, line, next_line, page))

    # --- 4️⃣ Extraire les descriptions, modalités et contrôles
    results = []
    for idx, (i, line, next_line, page) in enumerate(rubriques):
        start = i + 2
        end = rubriques[idx + 1][0] if idx + 1 < len(rubriques) else len(cleaned_lines)
        section_lines = [l for l, _ in cleaned_lines[start:end]]
        full_text = " ".join(section_lines).strip()

        # --- 🧩 Extraire les contrôles (CCH/SIG)
        regex_ctrl = r"(?:CCH|SIG)\s*-\s*\d+\s*:?.*?(?=(?:\s*(?:CCH|SIG)\s*-\s*\d+)|$)"
        controles = re.findall(regex_ctrl, full_text, flags=re.IGNORECASE | re.DOTALL)

        # --- Retirer les contrôles du texte de description
        without_ctrl = re.sub(regex_ctrl, " ", full_text, flags=re.IGNORECASE | re.DOTALL)

        # --- 🧩 Extraire les modalités (ex: '01 - texte')
        modalites = re.findall(
            r"\b0*(\d{1,2})\s*-\s*([^\d\[X]+?)(?=\s+\d{1,2}\s*-\s*|$)",
            without_ctrl
        )
        modalites = [(int(num), txt.strip()) for num, txt in modalites] if modalites else None

        # --- Retirer les modalités du texte principal
        cleaned_description = re.sub(
            r"\b0*\d{1,2}\s*-\s*[^\d\[X]+(?=\s+\d{1,2}\s*-\s*|$)",
            " ",
            without_ctrl
        )

        # --- Supprimer les marqueurs 'X [**,**]'
        cleaned_description = re.sub(r"\bX\s*\[\d+,\d+\]", " ", cleaned_description)

        # --- Nettoyage espaces multiples
        cleaned_description = re.sub(r"\s{2,}", " ", cleaned_description).strip()

        # --- 🧩 Extraire nom du champ + code DSN
        m = re.match(r"^(.*?)\s+(S\d{2}\.G\d{2}\.\d{2}\.\s*\d{3})$", line)
        nom_champ, code = (
            (m.group(1).strip(), m.group(2).replace(" ", "")) if m else (line, "")
        )

        # --- 📦 Stocker le résultat
        results.append({
            "page": page,
            "nom_champ": nom_champ,
            "code": code,
            "nom_technique": next_line,
            "description": cleaned_description,
            "modalites": modalites,
            "controles": [c.strip() for c in controles] or None,
        })

    return results


def rubriques_to_markdown(results):
    """
    Convertit une liste de rubriques DSN en texte Markdown.
    """
    md_blocks = []
    for r in results:
        bloc = (
            f"## {r['nom_champ']} (**{r['code']}**)\n\n"
            f"Nom technique: `{r['nom_technique']}`\n\n"
            f"{r['description'].strip()}\n"
        )
        md_blocks.append(bloc)
    return "\n\n".join(md_blocks)
