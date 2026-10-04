import pymupdf


def extract_pages_from_pdf(file_bytes: bytes) -> list[dict]:
    document = pymupdf.open(stream=file_bytes, filetype="pdf")

    pages = []

    for page_number, page in enumerate(document, start=1):
        pages.append(
            {
                "page": page_number,
                "text": page.get_text(),
            }
        )

    document.close()

    return pages
