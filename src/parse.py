import re

def detect_rubriques(text: str):
    """
    Détecte les rubriques (ligne avec code DSN Sxx.Gxx.xx.xxx en fin de ligne),
    récupère la ligne suivante (nom technique),
    et extrait la description entre cette rubrique et la suivante.
    Exclut toute ligne contenant CCH-<digits> ou SIG-<digits>.
    Associe à chaque rubrique le numéro de page détecté
    à partir des marqueurs === [PAGE X] ===.
    Détecte aussi les modalités (lignes ou séquences du type 'dd - texte'),
    puis les retire du champ 'description'.
    Nettoie également les marqueurs 'X [**,**]' restants.
    """

    # --- 1) Séparer et nettoyer les lignes
    lines = [listing.strip() for listing in text.splitlines() if listing.strip()]

    # --- 2) Préparer structures
    regex_page = r"^=== \[PAGE (\d+)\] ===$"
    regex_rubrique = r"S\d{2}\.G\d{2}\.\d{2}\.\s*\d{3}$"

    rubriques = []
    current_page = None
    cleaned_lines = []

    # --- 3) Identifier les pages et nettoyer les lignes
    for line in lines:
        m = re.match(regex_page, line)
        if m:
            current_page = int(m.group(1))
            continue  # on ne garde pas le marqueur dans le texte
        cleaned_lines.append((line, current_page))  # (contenu, page courante)

    # --- 4) Localiser les rubriques
    for i, (line, page) in enumerate(cleaned_lines):
        if re.search(regex_rubrique, line):
            # Exclure lignes contenant CCH-xxx ou SIG-xxx
            if re.search(r"(CCH-\d+|SIG-\d+)", line):
                continue

            if i + 1 < len(cleaned_lines):
                next_line, _ = cleaned_lines[i + 1]
                rubriques.append((i, line, next_line, page))

    # --- 5) Extraire les descriptions et les modalités
    results = []
    for idx, (i, line, next_line, page) in enumerate(rubriques):
        start = i + 2
        end = rubriques[idx + 1][0] if idx + 1 < len(rubriques) else len(cleaned_lines)
        section_lines = [l for l, _ in cleaned_lines[start:end]]

        full_text = " ".join(section_lines).strip()

        # --- 6) Extraire les modalités (motifs dd - texte)
        modalites = re.findall(
            r"\b0*(\d{1,2})\s*-\s*([^\d\[X]+?)(?=\s+\d{1,2}\s*-\s*|$)",
            full_text
        )
        modalites = [(int(num), txt.strip()) for num, txt in modalites] if modalites else None

        # --- 7) Nettoyer la description : retirer les modalités
        cleaned_description = re.sub(
            r"\b0*\d{1,2}\s*-\s*[^\d\[X]+(?=\s+\d{1,2}\s*-\s*|$)",
            " ",
            full_text
        )

        # --- 8) Supprimer les marqueurs 'X [**,**]'
        cleaned_description = re.sub(r"\bX\s*\[\d+,\d+\]", " ", cleaned_description)

        # Nettoyage final (espaces multiples)
        cleaned_description = re.sub(r"\s{2,}", " ", cleaned_description).strip()

        # --- 9) Extraire nom du champ + code DSN
        m = re.match(r"^(.*?)\s+(S\d{2}\.G\d{2}\.\d{2}\.\s*\d{3})$", line)
        nom_champ, code = (
            (m.group(1).strip(), m.group(2).replace(" ", "")) if m else (line, "")
        )

        results.append(
            {
                "page": page,
                "nom_champ": nom_champ,
                "code": code,
                "nom_technique": next_line,
                "description": cleaned_description,
                "modalites": modalites,
            }
        )

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
