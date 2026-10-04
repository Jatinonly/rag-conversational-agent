import re

# Headings like: "1. Title", "1) Title", or "2.3 Title"
HEADING_PATTERN = re.compile(r"^(\d+\.\d+(\.\d+)*|\d+[.)])\s+\S")


def is_heading(line):
    line = line.strip()

    if len(line) < 3:  # Heading cant be shorter than 3 chars
        return False
    if len(line) > 80:  # Heading cant be longer than 80 chars
        return False

    match = HEADING_PATTERN.match(line)
    if match is None:
        return False

    # Lines ending like any sentence are list items, not headings
    last_character = line[-1]
    if last_character in [".", ",", ";", ":"]:
        return False

    return True


def split_into_sections(text, starting_heading):
    """
    Produces something like:
    [
        {
            "heading": "1. Introduction",
            "body": "Running is a physical activity.\nIt improves cardiovascular fitness."
        },
        {
            "heading": "2. Benefits",
            "body": "Running improves heart health.\nIt also improves endurance."
        }
    ]
    """

    sections = []
    current_heading = starting_heading
    body_lines = []

    for line in text.splitlines():
        if is_heading(line):

            body = "\n".join(body_lines).strip()
            if body != "":
                sections.append({"heading": current_heading, "body": body})

            current_heading = line.strip()
            body_lines = []
        else:
            body_lines.append(line)

    # Save the final section of the page
    body = "\n".join(body_lines).strip()
    if body != "":
        sections.append({"heading": current_heading, "body": body})

    return {"sections": sections, "last_heading": current_heading}


def split_into_units(body):
    """Breaks text into sentences and bullet lines like:
    [
        "Running improves cardiovascular fitness.",
        "It improves endurance.",
        "Regular training is important.",
        "• Train three times per week.",
        "• Increase distance gradually."
    ]"""

    parts = re.split(r"(?<=[.!?])\s+|\n+", body)

    units = []
    for part in parts:
        cleaned = part.strip()
        if cleaned != "":
            units.append(cleaned)

    return units


def split_long_unit(unit, size):
    """If one sentence is longer than a chunk, break it."""
    if len(unit) <= size:
        return [unit]

    pieces = []
    current = ""

    for word in unit.split():
        if current == "":
            current = word
        elif len(current) + 1 + len(word) > size:
            pieces.append(current)
            current = word
        else:
            current = current + " " + word

    if current != "":
        pieces.append(current)

    return pieces


def pack_units(units, size, overlap):
    """
    Puts whole sentences into chunks until a chunk is full.
    The start of each new chunk repeats the last few sentences
    of the previous chunk (the overlap).
    """
    chunks = []
    current_units = []
    current_length = 0

    for unit in units:

        if len(current_units) > 0:
            extra = len(unit) + 1
        else:
            extra = len(unit)

        chunk_is_full = len(current_units) > 0 and current_length + extra > size

        if chunk_is_full:

            chunks.append("\n".join(current_units))

            carried_units = []
            carried_length = 0

            for old_unit in reversed(current_units):
                if carried_length + len(old_unit) + 1 > overlap:
                    break
                carried_units.insert(0, old_unit)
                carried_length = carried_length + len(old_unit) + 1

            if carried_length + len(unit) + 1 > size:
                carried_units = []
                carried_length = 0

            current_units = carried_units
            current_length = carried_length

            if len(current_units) > 0:
                extra = len(unit) + 1
            else:
                extra = len(unit)

        current_units.append(unit)
        current_length = current_length + extra

    if len(current_units) > 0:
        chunks.append("\n".join(current_units))

    return chunks


def chunk_document(pages, file_name, document_id, chunk_size=800, overlap=150):
    all_chunks = []
    current_heading = ""  # remembered across pages

    for page in pages:
        result = split_into_sections(page["text"], current_heading)
        sections = result["sections"]
        current_heading = result["last_heading"]

        for section in sections:
            section_heading = section["heading"]
            body = section["body"]

            if section_heading != "":
                room = chunk_size - len(section_heading) - 1
            else:
                room = chunk_size

            # Body into small units:
            units = []
            for unit in split_into_units(body):
                small_pieces = split_long_unit(unit, room)
                for piece in small_pieces:
                    units.append(piece)

            # Pack units into chunks, then add the heading on top
            text_pieces = pack_units(units, room, overlap)

            for piece in text_pieces:
                if section_heading != "":
                    full_text = section_heading + "\n" + piece
                else:
                    full_text = piece

                chunk = {
                    "text": full_text,
                    "page": page["page"],
                    "filename": file_name,
                    "document_id": document_id,
                }
                all_chunks.append(chunk)

    return all_chunks
