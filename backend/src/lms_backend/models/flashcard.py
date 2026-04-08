"""Models for flashcards."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Deck(SQLModel, table=True):
    """A deck of flashcards."""

    __tablename__ = "deck"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class Card(SQLModel, table=True):
    """A flashcard with question and answer."""

    __tablename__ = "card"

    id: int | None = Field(default=None, primary_key=True)
    deck_id: int = Field(default=None, foreign_key="deck.id")
    question: str
    answer: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class DeckCreate(SQLModel):
    """Schema for creating a deck."""

    name: str


class DeckRead(SQLModel):
    """Schema for reading a deck."""

    id: int
    user_id: int
    name: str
    created_at: datetime


class CardCreate(SQLModel):
    """Schema for creating a card."""

    question: str
    answer: str


class CardRead(SQLModel):
    """Schema for reading a card."""

    id: int
    deck_id: int
    question: str
    answer: str
    created_at: datetime


class DeckUpdate(SQLModel):
    """Schema for updating a deck."""

    name: str


class CardUpdate(SQLModel):
    """Schema for updating a card."""

    question: str
    answer: str
