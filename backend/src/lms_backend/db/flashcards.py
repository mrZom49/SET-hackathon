"""Database operations for flashcards."""

import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from lms_backend.models.flashcard import Card, Deck, DeckRead

logger = logging.getLogger(__name__)


async def read_decks(session: AsyncSession, user_id: int) -> list[DeckRead]:
    """Read all decks for a user from the database."""
    try:
        logger.info(
            "db_query",
            extra={"event": "db_query", "table": "deck", "operation": "select"},
        )
        result = await session.exec(select(DeckRead).where(DeckRead.user_id == user_id))
        return list(result.all())
    except Exception as exc:
        logger.error(
            "db_query",
            extra={
                "event": "db_query",
                "table": "deck",
                "operation": "select",
                "error": str(exc),
            },
        )
        raise


async def read_deck(session: AsyncSession, deck_id: int) -> Deck | None:
    """Read a single deck by id."""
    return await session.get(Deck, deck_id)


async def read_public_decks(session: AsyncSession) -> list[Deck]:
    """Read all public decks (not owned by current user)."""
    try:
        logger.info(
            "db_query",
            extra={"event": "db_query", "table": "deck", "operation": "select_public"},
        )
        result = await session.exec(select(Deck))
        return list(result.all())
    except Exception as exc:
        logger.error(
            "db_query",
            extra={
                "event": "db_query",
                "table": "deck",
                "operation": "select_public",
                "error": str(exc),
            },
        )
        raise


async def create_deck(session: AsyncSession, user_id: int, name: str) -> Deck:
    """Create a new deck in the database."""
    deck = Deck(user_id=user_id, name=name)
    session.add(deck)
    await session.commit()
    await session.refresh(deck)
    return deck


async def update_deck(session: AsyncSession, deck_id: int, name: str) -> Deck:
    """Update a deck's name."""
    deck = await session.get(Deck, deck_id)
    if deck is None:
        raise ValueError("Deck not found")
    deck.name = name
    await session.commit()
    await session.refresh(deck)
    return deck


async def delete_deck(session: AsyncSession, deck_id: int) -> bool:
    """Delete a deck and its cards from the database."""
    deck = await session.get(Deck, deck_id)
    if deck is None:
        return False
    await session.delete(deck)
    await session.commit()
    return True


async def read_cards(session: AsyncSession, deck_id: int) -> list[Card]:
    """Read all cards for a deck from the database."""
    try:
        logger.info(
            "db_query",
            extra={"event": "db_query", "table": "card", "operation": "select"},
        )
        result = await session.exec(select(Card).where(Card.deck_id == deck_id))
        return list(result.all())
    except Exception as exc:
        logger.error(
            "db_query",
            extra={
                "event": "db_query",
                "table": "card",
                "operation": "select",
                "error": str(exc),
            },
        )
        raise


async def read_card(session: AsyncSession, card_id: int) -> Card | None:
    """Read a single card by id."""
    return await session.get(Card, card_id)


async def create_card(
    session: AsyncSession, deck_id: int, question: str, answer: str
) -> Card:
    """Create a new card in the database."""
    card = Card(deck_id=deck_id, question=question, answer=answer)
    session.add(card)
    await session.commit()
    await session.refresh(card)
    return card


async def update_card(
    session: AsyncSession, card_id: int, question: str, answer: str
) -> Card:
    """Update a card's question and answer."""
    card = await session.get(Card, card_id)
    if card is None:
        raise ValueError("Card not found")
    card.question = question
    card.answer = answer
    await session.commit()
    await session.refresh(card)
    return card


async def delete_card(session: AsyncSession, card_id: int) -> bool:
    """Delete a card from the database."""
    card = await session.get(Card, card_id)
    if card is None:
        return False
    await session.delete(card)
    await session.commit()
    return True
