import requests
from pathlib import Path
import PyPDF2
import re

def download_pdf(url: str, filename: str = None):

    if filename is None:
        filename = Path(url).name  # Extract file name from URL

    response = requests.get(url, timeout=15)
    response.raise_for_status()  # Raise an exception for HTTP errors

    with open(filename, "wb") as f:
        f.write(response.content)



def read_pdf_from_page(filepath: str, start_page: int = 0, end_page: int = None):
    """
    Read and extract text from a PDF starting at a specific page.

    Args:
        filepath (str): Path to the PDF file.
        start_page (int): Page number to start from (0-indexed).
        end_page (int, optional): Page number to stop before (0-indexed, exclusive).
                                  If None, reads until the end of the document.
    """
    text = ""
    with open(filepath, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)

        # Validate page range
        start_page = max(0, start_page)
        end_page = end_page if end_page is not None else total_pages
        end_page = min(end_page, total_pages)

        for i in range(start_page, end_page):
            page_text = reader.pages[i].extract_text() or ""
            text += page_text

    return text


def clean_pdf_text(text: str) -> str:
    """
    Nettoie le texte extrait du PDF en supprimant les lignes d'en-tête
    du type 'Sxx.Gxx.xx   YYYY -MM-DD'.
    """
    # 1️⃣ Supprimer les lignes de type 'S10.G00.00   2025 -07-22'
    cleaned = re.sub(r"^\s*S\d{2}\.G\d{2}\.\d{2}\s+\d{4}\s*-\s*\d{2}\s*-\s*\d{2}\s*$", "", text, flags=re.MULTILINE)

    # 2️⃣ Supprimer les lignes vides multiples
    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)

    # 3️⃣ Supprimer les espaces de début/fin
    cleaned = cleaned.strip()

    return cleaned
