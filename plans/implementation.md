# Flashcards Project Plan

---

## Version 1: Core Flashcard Study

### Core Feature
**Study flashcards with flip interaction** - The one feature most valuable to end-users. Users see a question, think of the answer, then flip to reveal and self-grade.

### What It Does
- Create decks with a name
- Add cards (question + answer) to a deck
- Study a deck: see question, flip to see answer, mark "Know" or "Don't Know"
- Track cards seen in session

### Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (via SQLModel)
- **Client**: React web app (Vite)

### Database Schema
- `Deck`: id, name, created_at
- `Card`: id, deck_id, question, answer, created_at

### API Endpoints
- `POST /decks` - Create deck
- `GET /decks` - List decks
- `POST /decks/{id}/cards` - Add card
- `GET /decks/{id}/cards` - List cards in deck
- `POST /decks/{id}/study` - Start study session, returns cards
- `POST /cards/{id}/grade` - Grade card (know/don't know)

### Client Features
- Deck list view
- Add deck form
- Card list view (per deck)
- Add card form
- Study mode: card flip animation, grade buttons

### Deliverable
Functioning web app shown to TA for feedback. Not polished, but working.

---

## Version 2: Spaced Repetition + Deck Organization

### Improvements from Version 1

1. **Spaced Repetition Algorithm**
   - Track card mastery level (1-5)
   - "Don't Know" resets to level 1, "Know" increments
   - Study sessions prioritize low-level cards first

2. **Deck Organization**
   - Delete decks and cards
   - Edit existing cards

3. **TA Feedback Addressed**
   - (Placeholder - address specific feedback from TA)

### Deployment
- Deploy backend and frontend to production
- Make available for use via public URL

### New Database Schema
- `Card`: id, deck_id, question, answer, mastery_level (1-5), next_review, created_at

### New API Endpoints
- `PUT /cards/{id}` - Update card
- `DELETE /cards/{id}` - Delete card
- `DELETE /decks/{id}` - Delete deck

### Client Enhancements
- Edit/delete buttons on cards and decks
- Mastery indicator (dots or bar) on cards
- "Next review" sorting in study mode

---

## Why This Works

| Aspect | Version 1 | Version 2 |
|--------|-----------|-----------|
| **Simple** | One deck, add cards, study | Adds SRS logic |
| **Useful** | Basic studying | Actual learning tool |
| **Easy to explain** | "Digital flashcards" | "Flashcards that schedule themselves" |