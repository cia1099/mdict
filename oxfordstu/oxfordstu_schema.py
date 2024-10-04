import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Index,
    Enum,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase


class PartOfSpeech(enum.Enum):
    verb = 0
    noun = 1
    adjective = 2
    adverb = 3
    pronoun = 4
    preposition = 5
    conjunction = 6
    interjection = 7


class Base(DeclarativeBase):
    pass


class Word(Base):
    __tablename__ = "words"
    __table_args__ = (Index("UX_word", "word"),)
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True)


class Definition(Base):
    __tablename__ = "definitions"
    __table_args__ = (Index("UX_speech", "part_of_speech"),)
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    part_of_speech = Column(Enum(PartOfSpeech))
    inflection = Column(String)
    alphabet_us = Column(String)
    alphabet_uk = Column(String)
    audio_us = Column(String)
    audio_uk = Column(String)
    chinese = Column(String)


class Explanation(Base):
    __tablename__ = "explanations"
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    definition_id = Column(Integer, ForeignKey("definitions.id"), nullable=False)
    subscript = Column(String, nullable=True, default=None)
    explain = Column(String, nullable=False)
    create_at = Column(Integer, default=int(datetime.now().timestamp()))


class Example(Base):
    __tablename__ = "examples"
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    explanation_id = Column(Integer, ForeignKey("explanations.id"), nullable=False)
    example = Column(String)


if __name__ == "__main__":
    DB_URL = "sqlite:///oxfordstu.db"
    engine = create_engine(DB_URL, echo=False)
    Base.metadata.create_all(engine)
