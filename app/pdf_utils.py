from io import BytesIO
from typing import Tuple

from pypdf import PdfReader


def extract_pdf_text(content: bytes) -> Tuple[str, int]:
    reader = PdfReader(BytesIO(content))
    pages_text = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages_text.append(page_text)
    text = "\n".join(pages_text).strip()
    return text, len(reader.pages)
