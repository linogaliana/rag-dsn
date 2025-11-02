import re

import re

def detect_rubriques(text: str):
    """
    Détecte les rubriques (ligne avec code DSN Sxx.Gxx.xx.xxx en fin de ligne),
    récupère la ligne suivante (nom technique), et extrait la description entre rubriques.

    Points clés :
    - Garde le n° de page via les marqueurs === [PAGE X] ===
    - Insère un saut de ligne avant chaque CCH/SIG (tolère espaces autour du tiret)
    - Extrait d'abord les modalités (lignes 'dd - texte', en MULTILINE)
    - Puis extrait et retire les contrôles CCH/SIG
    - Nettoie 'X [**,**]' et espaces
    """

    # --- 1) Séparer et nettoyer les lignes
    lines = [listing.strip() for listing in text.splitlines() if listing.strip()]

    regex_page = r"^=== \[PAGE (\d+)\] ===$"
    regex_rubrique = r"S\d{2}\.G\d{2}\.\d{2}\.\s*\d{3}$"

    rubriques = []
    current_page = None
    cleaned_lines = []

    # --- 2) Identifier les pages et normaliser les lignes
    for line in lines:
        m = re.match(regex_page, line)
        if m:
            current_page = int(m.group(1))
            continue  # on ne garde pas le marqueur de page

        # Saut de ligne avant CCH/SIG (accepte CCH-11 ou CCH -11)
        line = re.sub(r"\s*(?=(?:CCH|SIG)\s*-\s*\d+)", "\n", line)

        cleaned_lines.append((line.strip(), current_page))  # (texte, page)

    # --- 3) Localiser les rubriques
    for i, (line, page) in enumerate(cleaned_lines):
        if re.search(regex_rubrique, line):
            # exclure les lignes de contrôle pures
            if re.search(r"(?:CCH|SIG)\s*-\s*\d+", line):
                continue
            if i + 1 < len(cleaned_lines):
                next_line, _ = cleaned_lines[i + 1]
                rubriques.append((i, line, next_line, page))

    # --- 4) Extraire descriptions, modalités, contrôles
    results = []
    for idx, (i, line, next_line, page) in enumerate(rubriques):
        start = i + 2
        end = rubriques[idx + 1][0] if idx + 1 < len(rubriques) else len(cleaned_lines)
        # ⬅️ On conserve les retours à la ligne ici
        section_lines = [l for l, _ in cleaned_lines[start:end]]
        full_text = "\n".join(section_lines).strip()

        # --- 4.1 Modalités (par ligne) : ^0*(dd) - (texte)$ (MULTILINE)
        # Exemple: "01 - envoi normal" / "02 - envoi néant"
        modalites = re.findall(
            r"^\s*0*(\d{1,2})\s*-\s*(.+?)\s*$",
            full_text,
            flags=re.MULTILINE
        )
        modalites = [(int(num), txt.strip()) for num, txt in modalites] or None

        # Retirer TOUTE la ligne des modalités de la description
        text_wo_modalites = re.sub(
            r"^\s*0*\d{1,2}\s*-\s*.+?$",
            " ",
            full_text,
            flags=re.MULTILINE
        )

        # --- 4.2 Contrôles CCH/SIG (après avoir retiré les modalités)
        regex_ctrl = r"(?:CCH|SIG)\s*-\s*\d+\s*:?.*?(?=(?:\s*(?:CCH|SIG)\s*-\s*\d+)|\Z)"
        controles = re.findall(regex_ctrl, text_wo_modalites, flags=re.IGNORECASE | re.DOTALL)

        # Retirer les contrôles du texte
        text_wo_ctrl = re.sub(regex_ctrl, " ", text_wo_modalites, flags=re.IGNORECASE | re.DOTALL)

        # --- 4.3 Nettoyages finaux
        # Remettre sur une ligne pour le nettoyage final
        cleaned_description = text_wo_ctrl.replace("\r", " ").replace("\n", " ")
        # Supprimer 'X [**,**]'
        cleaned_description = re.sub(r"\bX\s*\[\d+,\d+\]", " ", cleaned_description)
        # Espaces multiples
        cleaned_description = re.sub(r"\s{2,}", " ", cleaned_description).strip()

        # --- 4.4 Nom du champ + code DSN (code sans espaces)
        m = re.match(r"^(.*?)\s+(S\d{2}\.G\d{2}\.\d{2}\.\s*\d{3})$", line)
        nom_champ, code = (
            (m.group(1).strip(), m.group(2).replace(" ", "")) if m else (line, "")
        )

        # --- 4.5 Résultat
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
