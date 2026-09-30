import re  # regular-expression module.


def chunk_page(
    page_text: str,
    page_number: int,
    file_name: str,
    document_id: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    chunks = []

    sections = split_into_sections(page_text)

    for section in sections:
        start = 0

        while start < len(section):
            end = start + chunk_size

            chunk = section[start:end]

            chunks.append(
                {
                    "text": chunk,
                    "page": page_number,
                    "filename": file_name,
                    "document_id": document_id,
                }
            )

            start = end - overlap

    return chunks


def split_into_sections(text: str) -> list[str]:
    matches = list(
        re.finditer(
            r"(?m)^\d+\.\s+.+$",
            text,
        )
    )

    if not matches:
        return [text.strip()] if text.strip() else []

    sections = []

    for i, match in enumerate(matches):
        start = match.start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        section = text[start:end].strip()

        if section:
            sections.append(section)

    return sections
