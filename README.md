# Flashcards

A web-based flashcard app where students can create study decks, collaborate by browsing everyone's decks, and track their learning progress with flip-card study sessions, shuffle mode, and session summaries.

## Demo

**Dashboard — browse all decks from every user:**

![Dashboard showing all users' decks](https://via.placeholder.com/800x450/10b981/ffffff?text=Dashboard+%E2%80%94+All+Decks)

**Study Mode — flip cards, grade yourself, get a summary:**

![Study mode with flip card and shuffle toggle](https://via.placeholder.com/800x450/059669/ffffff?text=Study+Mode+%E2%80%94+Flip+Cards+%2B+Shuffle)

## Product Context

**End users:** Students preparing for exams, courses, or certifications who want a simple, shared space to create and study flashcard decks.

**Problem:** Most flashcard apps lock decks behind individual accounts — you can't browse or study decks created by others. There's no shared learning space where everyone benefits from everyone else's study materials.

**Our solution:** A single-page web app with two views:

- **Dashboard** — shows every user's decks for collaborative studying. Click any deck to review its cards and start a study session.
- **Flashcards** — your personal workspace. Create, edit, and delete your own decks and cards, then study them with flip-card animations, shuffle mode, and a session summary that tells you how many cards you know.

## Features

### Implemented

- **User authentication** — register and login with email/password, JWT token persisted in localStorage
- **Dashboard tab** — view all decks created by every user; click a deck to view its cards and start studying
- **Flashcards tab** — view only your own decks with full CRUD
  - Create, rename, and delete decks
  - Add cards with question/answer pairs
  - Edit deck names, delete decks (cascades to cards)
- **Study Mode**
  - 3D flip-card animation (click to reveal answer)
  - "Know" / "Don't Know" grading buttons appear after flipping
  - **Shuffle toggle** — Fisher-Yates shuffle before starting a session
  - **Session summary** — percentage score, known count, don't-know count, and total after completing a deck
  - Exit study at any time or return to deck from summary
- **RESTful API** with 10 flashcard endpoints (see table below)
- **Owner-based write permissions** — anyone can read decks and cards; only the owner can edit or delete
- **Docker Compose deployment** — backend, PostgreSQL, pgAdmin, React build, and Caddy reverse proxy
- **OpenTelemetry** tracing and structured logging
- **Swagger UI** interactive API documentation at `/docs`

### Not Yet Implemented

| Feature | Notes |
|---------|-------|
| Card-level edit/delete UI | Backend endpoints exist (`PUT`/`DELETE` on cards) but no frontend buttons |
| Search / filter decks | No text search or tag-based filtering in the UI |
| Pagination | All list endpoints return unbounded results |
| Deck sharing / collaboration | No way to transfer ownership or co-author a deck |
| Spaced repetition | Study order is linear (or shuffled), not spaced-repetition-based |
| User profile management | No password change or profile settings page |
| Public decks page in UI | `GET /flashcards/decks/public` exists in the backend but is not used by the frontend |
| Import / export decks | No CSV or JSON import/export for decks |

## Usage

1. Open the app in a browser at `http://localhost:42002`.
2. **Register or login** — enter an email and password, then click Register (first time) or Login.
3. Navigate to the **Flashcards** tab.
4. **Create a deck** — type a name and click "Create Deck".
5. **Add cards** — click the deck, fill in Question and Answer, then click "Add Card".
6. **Edit or delete a deck** — use the "Edit" or "Delete" buttons on each deck card.
7. **Study** — inside a deck:
   - Check **Shuffle** if you want cards in random order.
   - Click **Study (N cards)** to enter Study Mode.
   - Click the card to flip it and reveal the answer.
   - Click **Know** (green) or **Don't Know** (red) to grade yourself.
   - After all cards are graded, view your **session summary** with a percentage score.
8. **Dashboard** — switch to the Dashboard tab to see every user's decks. Click any deck to review its cards and study.
9. **Logout** — click the "Logout" button in the header.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login, returns JWT token |
| GET | `/auth/me` | Get current user info |
| GET | `/flashcards/decks` | Get all decks (visible to everyone) |
| GET | `/flashcards/decks/my` | Get only the current user's decks |
| POST | `/flashcards/decks` | Create a new deck |
| GET | `/flashcards/decks/{deck_id}/cards` | Get all cards for a deck |
| POST | `/flashcards/decks/{deck_id}/cards` | Create a new card |
| PUT | `/flashcards/decks/{deck_id}` | Update a deck name (owner only) |
| DELETE | `/flashcards/decks/{deck_id}` | Delete a deck (owner only) |
| PUT | `/flashcards/decks/{deck_id}/cards/{card_id}` | Update a card (owner only) |
| DELETE | `/flashcards/decks/{deck_id}/cards/{card_id}` | Delete a card (owner only) |

Interactive API docs are available at `/docs` when the server is running.

## Deployment

### Prerequisites

| Requirement | Version |
|-------------|---------|
| OS | Ubuntu 24.04 (or any Linux with Docker support) |
| Docker | 24+ (with Compose V2) |
| Network | Ports 42001–42004 must be available |

No Python, Node.js, or PostgreSQL need to be installed on the host — everything runs inside Docker containers.

### Step-by-Step

**1. Clone the repository:**

```sh
git clone <your-repo-url>
cd se-toolkit-lab-8
```

**2. Create the secret environment file:**

```sh
cp .env.docker.example .env.docker.secret
```

**3. Edit `.env.docker.secret`** and set the following required values:

```sh
# Empty string if outside university network (pull from Docker Hub directly)
REGISTRY_PREFIX_DOCKER_HUB=

# PostgreSQL
POSTGRES_PASSWORD=<your-database-password>

# pgAdmin
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=<your-pgadmin-password>

# Gateway
GATEWAY_HOST_PORT=42002
LMS_API_KEY=<your-api-key>

# JWT authentication
JWT_SECRET=<generate-a-random-secret-key>

# Autochecker API (required for ETL pipeline)
AUTOCHECKER_API_URL=https://auche.namaz.live
AUTOCHECKER_API_LOGIN=<your-login>
AUTOCHECKER_API_PASSWORD=<your-password>
```

Generate a JWT secret with:

```sh
python3 -c "import secrets; print(secrets.token_hex(32))"
```

All other values in the file have sensible defaults.

**4. Build and start all services:**

```sh
docker compose --env-file .env.docker.secret up -d --build
```

This starts 5 containers:

| Service | Port | Purpose |
|---------|------|---------|
| caddy | 42002 | Reverse proxy + serves the React SPA |
| backend | 42001 | FastAPI application |
| postgres | 42004 | PostgreSQL database |
| pgadmin | 42003 | pgAdmin web UI |
| client-web-react | — | Build stage (outputs static files for Caddy) |

**5. Verify services:**

```sh
docker compose --env-file .env.docker.secret ps
```

All containers should show `Up` status. PostgreSQL will show `healthy`.

**6. Access the application:**

| Service | URL |
|---------|-----|
| Frontend (Flashcards) | `http://<host-ip>:42002` |
| Backend API | `http://<host-ip>:42001` |
| Swagger UI | `http://<host-ip>:42002/docs` |
| pgAdmin | `http://<host-ip>:42003` |

**7. Stop services:**

```sh
docker compose --env-file .env.docker.secret down
```

**8. Stop and wipe all data (removes database volumes):**

```sh
docker compose --env-file .env.docker.secret down -v
```
