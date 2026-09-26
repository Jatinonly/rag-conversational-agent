
def chunk_page(
    page_text: str,
    page_number: int,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    chunks = []

    start = 0

    while start < len(page_text):
        end = start + chunk_size

        chunk = page_text[start:end]

        chunks.append({
            "text": chunk,
            "page": page_number,
        })

        start = end - overlap

    return chunks
