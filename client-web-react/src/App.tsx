import { useState, useEffect, FormEvent } from 'react'
import './App.css'

const STORAGE_KEY = 'auth_token'

type Page = 'dashboard' | 'flashcards'

interface Deck {
  id: number
  name: string
  created_at: string
}

interface Card {
  id: number
  deck_id: number
  question: string
  answer: string
  created_at: string
}

function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem(STORAGE_KEY) ?? '',
  )
  const [page, setPage] = useState<Page>('dashboard')

  if (!token) {
    return <AuthPage onLogin={(t) => {
      localStorage.setItem(STORAGE_KEY, t)
      setToken(t)
    }} />
  }

  return (
    <div>
      <header className="app-header">
        <nav className="nav-links">
          <button
            className={page === 'dashboard' ? 'nav-active' : ''}
            onClick={() => setPage('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={page === 'flashcards' ? 'nav-active' : ''}
            onClick={() => setPage('flashcards')}
          >
            Flashcards
          </button>
        </nav>
        <div className="user-info">
          <button className="btn-disconnect" onClick={() => {
            localStorage.removeItem(STORAGE_KEY)
            setToken('')
          }}>
            Logout
          </button>
        </div>
      </header>

      {page === 'dashboard' && <DashboardPage token={token} />}
      {page === 'flashcards' && <FlashcardsPage token={token} />}
    </div>
  )
}

function AuthPage({ onLogin }: { onLogin: (token: string) => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/register'
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Authentication failed')
      }
      const data = await res.json()
      onLogin(data.access_token)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="token-form" onSubmit={handleSubmit}>
      <h1>{mode === 'login' ? 'Login' : 'Register'}</h1>
      <p>Enter your credentials to access flashcards.</p>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Loading...' : mode === 'login' ? 'Login' : 'Register'}
      </button>
      <p className="switch-mode">
        {mode === 'login' ? "Don't have an account? " : "Already have an account? "}
        <button type="button" className="link-btn" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
          {mode === 'login' ? 'Register' : 'Login'}
        </button>
      </p>
    </form>
  )
}

function DashboardPage({ token }: { token: string }) {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadDecks = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/flashcards/decks', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `HTTP ${res.status}`)
      }
      const data: Deck[] = await res.json()
      setDecks(data)
    } catch (err) {
      console.error('Load decks error:', err)
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDecks()
  }, [])

  return (
    <div className="dashboard-container">
      <h1>Dashboard</h1>
      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}
      <div className="deck-list">
        {decks.map((deck) => (
          <div key={deck.id} className="deck-card">
            <h3>{deck.name}</h3>
            <p>Created: {new Date(deck.created_at).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function FlashcardsPage({ token }: { token: string }) {
  const [decks, setDecks] = useState<Deck[]>([])
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null)
  const [cards, setCards] = useState<Card[]>([])
  const [studyCards, setStudyCards] = useState<Card[]>([])
  const [studyIndex, setStudyIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [isResetting, setIsResetting] = useState(false)
  const [showStudy, setShowStudy] = useState(false)
  const [newDeckName, setNewDeckName] = useState('')
  const [newQuestion, setNewQuestion] = useState('')
  const [newAnswer, setNewAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadDecks = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/flashcards/decks', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `HTTP ${res.status}`)
      }
      const data: Deck[] = await res.json()
      setDecks(data)
    } catch (err) {
      console.error('Load decks error:', err)
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const loadCards = async (deckId: number) => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`/flashcards/decks/${deckId}/cards`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `HTTP ${res.status}`)
      }
      const data: Card[] = await res.json()
      setCards(data)
    } catch (err) {
      console.error('Load cards error:', err)
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDecks()
  }, [])

  const createDeck = async (e: FormEvent) => {
    e.preventDefault()
    if (!newDeckName.trim()) return
    try {
      const res = await fetch('/flashcards/decks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newDeckName }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `HTTP ${res.status}`)
      }
      setNewDeckName('')
      loadDecks()
    } catch (err) {
      console.error('Create deck error:', err)
      setError((err as Error).message)
    }
  }

  const createCard = async (e: FormEvent) => {
    e.preventDefault()
    if (!selectedDeck || !newQuestion.trim() || !newAnswer.trim()) return
    try {
      const res = await fetch(`/flashcards/decks/${selectedDeck.id}/cards`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: newQuestion, answer: newAnswer }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `HTTP ${res.status}`)
      }
      setNewQuestion('')
      setNewAnswer('')
      loadCards(selectedDeck.id)
    } catch (err) {
      console.error('Create card error:', err)
      setError((err as Error).message)
    }
  }

  const deleteDeck = async (deckId: number) => {
    try {
      const res = await fetch(`/flashcards/decks/${deckId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `HTTP ${res.status}`)
      }
      if (selectedDeck?.id === deckId) setSelectedDeck(null)
      loadDecks()
    } catch (err) {
      console.error('Delete deck error:', err)
      setError((err as Error).message)
    }
  }

  const updateDeck = async (deckId: number, newName: string) => {
    try {
      const res = await fetch(`/flashcards/decks/${deckId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newName }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `HTTP ${res.status}`)
      }
      loadDecks()
      if (selectedDeck?.id === deckId) {
        setSelectedDeck({ ...selectedDeck, name: newName })
      }
    } catch (err) {
      console.error('Update deck error:', err)
      setError((err as Error).message)
    }
  }

  const startStudy = () => {
    if (cards.length === 0) return
    setStudyCards([...cards])
    setStudyIndex(0)
    setIsFlipped(false)
    setShowStudy(true)
  }

  const gradeCard = () => {
    setIsResetting(true)
    setIsFlipped(false)
    setTimeout(() => {
      if (studyIndex < studyCards.length - 1) {
        setStudyIndex(studyIndex + 1)
      } else {
        setShowStudy(false)
      }
      setIsResetting(false)
    }, 300)
  }

  if (showStudy && studyCards.length > 0) {
    const currentCard = studyCards[studyIndex]
    return (
      <div className="flashcards-container">
        <div className="study-mode">
          <h2>Study Mode ({studyIndex + 1}/{studyCards.length})</h2>
          <div
            className={`flashcard ${isFlipped ? 'flipped' : ''} ${isResetting ? 'resetting' : ''}`}
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <div className="flashcard-inner">
              <div className="flashcard-front">
                <p>{currentCard.question}</p>
                <span className="flip-hint">Click to flip</span>
              </div>
              <div className="flashcard-back">
                <p>{currentCard.answer}</p>
              </div>
            </div>
          </div>
          {isFlipped && (
            <div className="grade-buttons">
              <button className="btn-know" onClick={gradeCard}>
                Know
              </button>
              <button className="btn-dont-know" onClick={gradeCard}>
                Don't Know
              </button>
            </div>
          )}
          <button className="btn-back" onClick={() => setShowStudy(false)}>
            Exit Study
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flashcards-container">
      <h1>Flashcards</h1>
      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}

      {!selectedDeck ? (
        <div className="decks-section">
          <h2>Your Decks</h2>
          <form onSubmit={createDeck} className="create-form">
            <input
              type="text"
              placeholder="Deck name"
              value={newDeckName}
              onChange={(e) => setNewDeckName(e.target.value)}
            />
            <button type="submit">Create Deck</button>
          </form>
          <div className="deck-list">
            {decks.map((deck) => (
              <div
                key={deck.id}
                className="deck-card"
                onClick={() => {
                  setSelectedDeck(deck)
                  loadCards(deck.id)
                }}
              >
                <h3>{deck.name}</h3>
                <p>Created: {new Date(deck.created_at).toLocaleDateString()}</p>
                <div className="deck-actions">
                  <button
                    className="btn-edit"
                    onClick={(e) => {
                      e.stopPropagation()
                      const newName = prompt('Enter new deck name:', deck.name)
                      if (newName && newName !== deck.name) {
                        updateDeck(deck.id, newName)
                      }
                    }}
                  >
                    Edit
                  </button>
                  <button
                    className="btn-delete"
                    onClick={(e) => {
                      e.stopPropagation()
                      if (confirm('Delete this deck and all its cards?')) {
                        deleteDeck(deck.id)
                      }
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="cards-section">
          <button className="btn-back" onClick={() => setSelectedDeck(null)}>
            Back to Decks
          </button>
          <h2>{selectedDeck.name}</h2>
          <form onSubmit={createCard} className="create-form">
            <input
              type="text"
              placeholder="Question"
              value={newQuestion}
              onChange={(e) => setNewQuestion(e.target.value)}
            />
            <input
              type="text"
              placeholder="Answer"
              value={newAnswer}
              onChange={(e) => setNewAnswer(e.target.value)}
            />
            <button type="submit">Add Card</button>
          </form>
          <button
            className="btn-study"
            onClick={startStudy}
            disabled={cards.length === 0}
          >
            Study ({cards.length} cards)
          </button>
          <div className="card-list">
            {cards.map((card) => (
              <div key={card.id} className="card-item">
                <div className="card-question">
                  <strong>Q:</strong> {card.question}
                </div>
                <div className="card-answer">
                  <strong>A:</strong> {card.answer}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App