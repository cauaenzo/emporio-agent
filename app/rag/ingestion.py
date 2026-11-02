
import pymupdf

from app.config import DATA_FILES


class PDFIngestion:
    """Extrai e divide o conteúdo textual do manual."""

    def extract_pages(self) -> list[dict]:
        document = pymupdf.open(DATA_FILES["policies"])
        pages = []

        try:
            for page_number, page in enumerate(document, start=1):
                # A primeira página é apenas a capa.
                if page_number == 1:
                    continue

                text = page.get_text("text").strip()

                if text:
                    pages.append({
                        "page": page_number,
                        "text": text,
                    })
        finally:
            document.close()

        return pages

    def create_chunks(
        self,
        chunk_size: int = 110,
        overlap: int = 20,
    ) -> list[dict]:

        if chunk_size <= 0:
            raise ValueError("O tamanho do chunk deve ser positivo.")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("O overlap deve ser menor que o chunk.")

        chunks = []

        for page in self.extract_pages():
            words = page["text"].split()
            start = 0

            while start < len(words):
                end = min(start + chunk_size, len(words))

                chunks.append({
                    "pages": [page["page"]],
                    "text": " ".join(words[start:end]),
                })

                if end >= len(words):
                    break

                start = end - overlap

        return chunks
