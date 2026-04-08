"""Router for flashcard endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from lms_backend.auth import UserDep
from lms_backend.database import get_session
from lms_backend.db.flashcards import (
    create_card,
    create_deck,
    delete_card,
    delete_deck,
    read_card,
    read_cards,
    read_deck,
    read_public_decks,
    update_card,
    update_deck,
)
from lms_backend.models.flashcard import (
    CardCreate,
    CardRead,
    CardUpdate,
    Deck,
    DeckCreate,
    DeckRead,
    DeckUpdate,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/decks", response_model=list[DeckRead])
async def get_decks(user: UserDep, session: AsyncSession = Depends(get_session)):
    """Get all decks for the current user."""
    user_id = user.id
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID not found",
        )
    try:
        result = await session.exec(select(Deck).where(Deck.user_id == user_id))
        return list(result.all())
    except Exception as exc:
        logger.warning(
            "decks_list_failed",
            extra={"event": "decks_list_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend error: {exc}",
        ) from exc


@router.post("/decks", response_model=DeckRead, status_code=201)
async def post_deck(
    body: DeckCreate, user: UserDep, session: AsyncSession = Depends(get_session)
):
    """Create a new deck for the current user."""
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID not found",
        )
    try:
        return await create_deck(session, user_id=user.id, name=body.name)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Failed to create deck",
        )


@router.get("/decks/{deck_id}/cards", response_model=list[CardRead])
async def get_cards(
    deck_id: int, user: UserDep, session: AsyncSession = Depends(get_session)
):
    """Get all cards for a deck."""
    deck = await read_deck(session, deck_id)
    if deck is None or deck.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found"
        )
    try:
        return await read_cards(session, deck_id)
    except Exception as exc:
        logger.warning(
            "cards_list_failed",
            extra={"event": "cards_list_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend error: {exc}",
        ) from exc


@router.post("/decks/{deck_id}/cards", response_model=CardRead, status_code=201)
async def post_card(
    deck_id: int,
    body: CardCreate,
    user: UserDep,
    session: AsyncSession = Depends(get_session),
):
    """Create a new card in a deck."""
    deck = await read_deck(session, deck_id)
    if deck is None or deck.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found"
        )
    try:
        return await create_card(session, deck_id, body.question, body.answer)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Failed to create card",
        )


@router.get("/decks/public", response_model=list[DeckRead])
async def get_public_decks(session: AsyncSession = Depends(get_session)):
    """Get all public decks (decks from other users)."""
    try:
        return await read_public_decks(session)
    except Exception as exc:
        logger.warning(
            "public_decks_list_failed",
            extra={"event": "public_decks_list_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend error: {exc}",
        ) from exc


@router.put("/decks/{deck_id}", response_model=DeckRead)
async def put_deck(
    deck_id: int,
    body: DeckUpdate,
    user: UserDep,
    session: AsyncSession = Depends(get_session),
):
    """Update a deck (only owner can update)."""
    deck = await read_deck(session, deck_id)
    if deck is None or deck.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found"
        )
    try:
        return await update_deck(session, deck_id, body.name)
    except Exception as exc:
        logger.warning(
            "deck_update_failed",
            extra={"event": "deck_update_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend error: {exc}",
        ) from exc


@router.delete("/decks/{deck_id}", status_code=204)
async def delete_deck_endpoint(
    deck_id: int,
    user: UserDep,
    session: AsyncSession = Depends(get_session),
):
    """Delete a deck (only owner can delete)."""
    deck = await read_deck(session, deck_id)
    if deck is None or deck.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found"
        )
    try:
        await delete_deck(session, deck_id)
    except Exception as exc:
        logger.warning(
            "deck_delete_failed",
            extra={"event": "deck_delete_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend error: {exc}",
        ) from exc


@router.put("/decks/{deck_id}/cards/{card_id}", response_model=CardRead)
async def put_card(
    deck_id: int,
    card_id: int,
    body: CardUpdate,
    user: UserDep,
    session: AsyncSession = Depends(get_session),
):
    """Update a card (only deck owner can update)."""
    deck = await read_deck(session, deck_id)
    if deck is None or deck.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found"
        )
    card = await read_card(session, card_id)
    if card is None or card.deck_id != deck_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )
    try:
        return await update_card(session, card_id, body.question, body.answer)
    except Exception as exc:
        logger.warning(
            "card_update_failed",
            extra={"event": "card_update_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend error: {exc}",
        ) from exc


@router.delete("/decks/{deck_id}/cards/{card_id}", status_code=204)
async def delete_card_endpoint(
    deck_id: int,
    card_id: int,
    user: UserDep,
    session: AsyncSession = Depends(get_session),
):
    """Delete a card (only deck owner can delete)."""
    deck = await read_deck(session, deck_id)
    if deck is None or deck.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found"
        )
    card = await read_card(session, card_id)
    if card is None or card.deck_id != deck_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )
    try:
        await delete_card(session, card_id)
    except Exception as exc:
        logger.warning(
            "card_delete_failed",
            extra={"event": "card_delete_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend error: {exc}",
        ) from exc
