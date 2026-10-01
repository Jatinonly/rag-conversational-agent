from sqlalchemy import create_engine, String, Text, Integer, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

DATABASE_URL = "sqlite:///./rag.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# DeclarativeBase → base class for your database models.
# Mapped → tells Python/SQLAlchemy what type of data a field contains.
# mapped_column → defines an actual database column.


# Create a new class called "Base" that inherits from "DeclarativeBase".
class Base(DeclarativeBase):
    # "pass" means Don't put any additional code inside this class for now.
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",  # Creates a two-way relationship
        cascade="all, delete-orphan",  # This does-If a Document is deleted, its associated Chunks are also deleted.
    )

    # documents table looks like: (NOTE- chunks is not a column but a attribute)
    # -------------------------
    # id          TEXT   PK
    # filename    TEXT   NOT NULL


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[int] = mapped_column(Integer, nullable=False)

    document: Mapped["Document"] = relationship(back_populates="chunks")


Base.metadata.create_all(engine)
