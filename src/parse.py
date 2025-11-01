import re


def detect_rubriques(text: str):
    """
    Détecte les rubriques (ligne avec code DSN Sxx.Gxx.xx.xxx en fin de ligne),
    récupère la ligne suivante (nom technique),
    et extrait la description entre cette rubrique et la suivante.
    Exclut toute ligne contenant CCH-<digits> ou SIG-<digits>.
    """
    # 1) Split + strip
    lines = [listing.strip() for listing in text.splitlines() if listing.strip()]

    # 3) Regex rubrique (code DSN à la fin de la ligne)
    regex_rubrique = r"S\d{2}\.G\d{2}\.\d{2}\.\s*\d{3}$"

    # 4) Localiser les rubriques + capturer la ligne suivante (nom technique)
    rubriques = []
    for i, line in enumerate(lines):
        if re.search(regex_rubrique, line) and i + 1 < len(lines):
            rubriques.append((i, line, lines[i + 1]))

    # 5) Extraire le texte entre deux rubriques
    results = []
    for idx, (i, line, next_line) in enumerate(rubriques):
        start = i + 2
        end = rubriques[idx + 1][0] if idx + 1 < len(rubriques) else len(lines)
        description = " ".join(lines[start:end]).strip()

        m = re.match(r"^(.*?)\s+(S\d{2}\.G\d{2}\.\d{2}\.\s*\d{3})$", line)
        nom_champ, code = (
            (m.group(1).strip(), m.group(2).replace(" ", "")) if m else (line, "")
        )

        results.append(
            {
                "nom_champ": nom_champ,
                "code": code,
                "nom_technique": next_line,
                "description": description,
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
