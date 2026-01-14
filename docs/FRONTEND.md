# Frontend Integration Guide

How to integrate the Focus Group Chat API into your website.

## Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Your Frontend                        │
│  ┌─────────────┐     ┌─────────────┐    ┌───────────┐  │
│  │   Chat UI   │────▶│   State     │───▶│ localStorage│  │
│  │  Component  │◀────│  (history)  │◀───│  (persist)  │  │
│  └─────────────┘     └─────────────┘    └───────────┘  │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP/JSON
                           ▼
              ┌────────────────────────────┐
              │    Focus Group API         │
              │  https://api.vercel.app    │
              └────────────────────────────┘
```

**Key Concept:** Your frontend manages conversation history. The API is stateless.

---

## Quick Start

### 1. Fetch Utility

```typescript
const API_URL = 'https://your-api.vercel.app';

async function askFocusGroup(
  audienceId: string,
  question: string,
  history: Message[] = []
) {
  const res = await fetch(`${API_URL}/audiences/${audienceId}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history })
  });

  if (!res.ok) throw new Error('API error');
  return res.json();
}
```

### 2. Use It

```typescript
// First question
let history = [];
const result = await askFocusGroup('premium_chocolate', 'What do you think?');
history = result.history;

// Follow-up (include history)
const result2 = await askFocusGroup('premium_chocolate', 'Tell me more', history);
history = result2.history;
```

---

## TypeScript Types

```typescript
// Message in conversation history
interface Message {
  role: 'moderator' | 'persona';
  text: string;
  persona_id: number | null;
  persona_name: string | null;
}

// Response from a persona
interface PersonaResponse {
  persona_id: number;
  persona_name: string;
  text: string;
}

// Persona details
interface Persona {
  id: number;
  name: string;
  age: number;
  occupation: string;
  location: string;
  backstory: string;
  category_relationship: string;
  personality_traits: string[];
  speech_patterns: string[];
}

// API Responses
interface AskGroupResponse {
  responses: PersonaResponse[];
  history: Message[];
}

interface AskPersonaResponse {
  response: PersonaResponse;
  history: Message[];
}

interface AudienceDetails {
  id: string;
  category: string;
  description: string;
  personas: Persona[];
}
```

---

## React Hook

Complete hook for managing focus group state:

```typescript
// useFocusGroup.ts
import { useState, useEffect, useCallback } from 'react';

const API_URL = 'https://your-api.vercel.app';

interface UseFocusGroupOptions {
  persistKey?: string;  // localStorage key for persistence
}

export function useFocusGroup(
  audienceId: string,
  options: UseFocusGroupOptions = {}
) {
  const { persistKey } = options;

  // State
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [history, setHistory] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load persisted history on mount
  useEffect(() => {
    if (persistKey) {
      const saved = localStorage.getItem(persistKey);
      if (saved) {
        try {
          setHistory(JSON.parse(saved));
        } catch {}
      }
    }
  }, [persistKey]);

  // Save history on change
  useEffect(() => {
    if (persistKey && history.length > 0) {
      localStorage.setItem(persistKey, JSON.stringify(history));
    }
  }, [history, persistKey]);

  // Load audience details
  useEffect(() => {
    fetch(`${API_URL}/audiences/${audienceId}`)
      .then(res => res.json())
      .then(data => setPersonas(data.personas))
      .catch(err => setError(err.message));
  }, [audienceId]);

  // Ask the group
  const askGroup = useCallback(async (question: string) => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/audiences/${audienceId}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, history })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'API error');
      }

      const data: AskGroupResponse = await res.json();
      setHistory(data.history);
      return data.responses;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [audienceId, history]);

  // Ask specific persona (1:1)
  const askPersona = useCallback(async (personaId: number, question: string) => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/audiences/${audienceId}/ask/${personaId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, history })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'API error');
      }

      const data: AskPersonaResponse = await res.json();
      setHistory(data.history);
      return data.response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [audienceId, history]);

  // Reset conversation
  const reset = useCallback(() => {
    setHistory([]);
    if (persistKey) {
      localStorage.removeItem(persistKey);
    }
  }, [persistKey]);

  // Get specific persona by ID
  const getPersona = useCallback((id: number) => {
    return personas.find(p => p.id === id);
  }, [personas]);

  return {
    // State
    personas,
    history,
    loading,
    error,

    // Actions
    askGroup,
    askPersona,
    reset,
    getPersona
  };
}
```

---

## React Component Example

```tsx
// FocusGroupChat.tsx
import { useState, FormEvent } from 'react';
import { useFocusGroup } from './useFocusGroup';

interface Props {
  audienceId: string;
}

export function FocusGroupChat({ audienceId }: Props) {
  const {
    personas,
    history,
    loading,
    error,
    askGroup,
    askPersona,
    reset
  } = useFocusGroup(audienceId, {
    persistKey: `focus-group-${audienceId}`
  });

  const [input, setInput] = useState('');
  const [selectedPersona, setSelectedPersona] = useState<number | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    try {
      if (selectedPersona) {
        await askPersona(selectedPersona, input);
        setSelectedPersona(null);
      } else {
        await askGroup(input);
      }
      setInput('');
    } catch {
      // Error already in state
    }
  };

  return (
    <div className="focus-group">
      {/* Error banner */}
      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      )}

      {/* Persona sidebar */}
      <aside className="persona-sidebar">
        <h3>Participants</h3>
        {personas.map(p => (
          <div
            key={p.id}
            className={`persona-card ${selectedPersona === p.id ? 'selected' : ''}`}
            onClick={() => setSelectedPersona(
              selectedPersona === p.id ? null : p.id
            )}
          >
            <strong>{p.name}</strong>, {p.age}
            <p>{p.occupation}</p>
            <small>{p.location}</small>
          </div>
        ))}
        {history.length > 0 && (
          <button onClick={reset} className="reset-btn">
            New Session
          </button>
        )}
      </aside>

      {/* Chat area */}
      <main className="chat-area">
        <div className="messages">
          {history.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <strong>
                {msg.role === 'moderator' ? 'You' : msg.persona_name}:
              </strong>
              <p>{msg.text}</p>
            </div>
          ))}

          {loading && (
            <div className="message loading">
              <span className="typing-indicator">Thinking...</span>
            </div>
          )}
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="input-form">
          {selectedPersona && (
            <div className="addressing">
              Asking {personas.find(p => p.id === selectedPersona)?.name}
              <button type="button" onClick={() => setSelectedPersona(null)}>×</button>
            </div>
          )}
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={
              selectedPersona
                ? `Ask ${personas.find(p => p.id === selectedPersona)?.name}...`
                : "Ask the group..."
            }
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
```

---

## Vanilla JavaScript

```javascript
// focus-group.js
const API_URL = 'https://your-api.vercel.app';

class FocusGroupClient {
  constructor(audienceId) {
    this.audienceId = audienceId;
    this.history = [];
    this.personas = [];
  }

  async loadAudience() {
    const res = await fetch(`${API_URL}/audiences/${this.audienceId}`);
    const data = await res.json();
    this.personas = data.personas;
    return this.personas;
  }

  async askGroup(question) {
    const res = await fetch(`${API_URL}/audiences/${this.audienceId}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, history: this.history })
    });

    if (!res.ok) throw new Error('API error');

    const data = await res.json();
    this.history = data.history;
    return data.responses;
  }

  async askPersona(personaId, question) {
    const res = await fetch(`${API_URL}/audiences/${this.audienceId}/ask/${personaId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, history: this.history })
    });

    if (!res.ok) throw new Error('API error');

    const data = await res.json();
    this.history = data.history;
    return data.response;
  }

  reset() {
    this.history = [];
  }

  saveToStorage(key) {
    localStorage.setItem(key, JSON.stringify(this.history));
  }

  loadFromStorage(key) {
    const saved = localStorage.getItem(key);
    if (saved) {
      this.history = JSON.parse(saved);
    }
  }
}

// Usage
const fg = new FocusGroupClient('premium_chocolate');
await fg.loadAudience();

const responses = await fg.askGroup('What do you think of premium chocolate?');
responses.forEach(r => {
  console.log(`${r.persona_name}: ${r.text}`);
});
```

---

## Persistence

### Option 1: localStorage (simple)

```typescript
// Save after each response
useEffect(() => {
  if (history.length > 0) {
    localStorage.setItem('focus-group-history', JSON.stringify(history));
  }
}, [history]);

// Load on mount
useEffect(() => {
  const saved = localStorage.getItem('focus-group-history');
  if (saved) setHistory(JSON.parse(saved));
}, []);
```

### Option 2: Your Backend

```typescript
// Save to your database
async function saveSession(sessionId: string, history: Message[]) {
  await fetch('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({ sessionId, history })
  });
}

// Load from database
async function loadSession(sessionId: string): Promise<Message[]> {
  const res = await fetch(`/api/sessions/${sessionId}`);
  const data = await res.json();
  return data.history;
}
```

---

## Error Handling

```typescript
const askGroup = async (question: string) => {
  try {
    const res = await fetch(`${API_URL}/audiences/${audienceId}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, history })
    });

    if (!res.ok) {
      const error = await res.json();

      // Handle specific errors
      if (res.status === 404) {
        throw new Error(`Audience "${audienceId}" not found`);
      }
      if (res.status === 504) {
        throw new Error('Request timed out. Please try again.');
      }

      throw new Error(error.detail || 'Unknown error');
    }

    return await res.json();
  } catch (err) {
    if (err instanceof TypeError) {
      // Network error
      throw new Error('Network error. Check your connection.');
    }
    throw err;
  }
};
```

---

## Loading States

### Simple Spinner

```tsx
{loading && <div className="spinner">Loading...</div>}
```

### Typing Indicator

```tsx
{loading && (
  <div className="typing">
    <span className="dot"></span>
    <span className="dot"></span>
    <span className="dot"></span>
  </div>
)}
```

```css
.typing .dot {
  animation: bounce 1.4s infinite;
  background: #666;
  border-radius: 50%;
  display: inline-block;
  height: 8px;
  margin: 0 2px;
  width: 8px;
}
.typing .dot:nth-child(2) { animation-delay: 0.2s; }
.typing .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}
```

### Optimistic UI

Show the question immediately while waiting:

```tsx
const askGroup = async (question: string) => {
  // Optimistically add question to history
  const optimisticHistory = [
    ...history,
    { role: 'moderator', text: question, persona_id: null, persona_name: null }
  ];
  setHistory(optimisticHistory);
  setLoading(true);

  try {
    const res = await fetch(...);
    const data = await res.json();
    setHistory(data.history);  // Replace with actual
  } catch {
    // Rollback on error
    setHistory(history);
  } finally {
    setLoading(false);
  }
};
```

---

## Styling Tips

### Chat Bubbles

```css
.message {
  margin: 12px 0;
  max-width: 80%;
}

.message.moderator {
  background: #e3f2fd;
  border-radius: 16px 16px 16px 4px;
  margin-left: auto;
  padding: 12px 16px;
}

.message.persona {
  background: #f5f5f5;
  border-radius: 16px 16px 4px 16px;
  padding: 12px 16px;
}

.message.persona strong {
  color: #1976d2;
  display: block;
  font-size: 0.85em;
  margin-bottom: 4px;
}
```

### Persona Cards

```css
.persona-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 8px;
  padding: 12px;
  transition: all 0.2s;
}

.persona-card:hover {
  border-color: #1976d2;
}

.persona-card.selected {
  background: #e3f2fd;
  border-color: #1976d2;
}

.persona-card strong {
  display: block;
  font-size: 1.1em;
}

.persona-card p {
  color: #666;
  font-size: 0.9em;
  margin: 4px 0 0 0;
}
```

---

## Advanced: Streaming Responses

The API doesn't support streaming, but you can simulate it:

```typescript
// Typewriter effect for responses
function TypewriterMessage({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState('');

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 20);

    return () => clearInterval(interval);
  }, [text]);

  return <p>{displayed}</p>;
}
```

---

## Complete Example

See `focus_group/README.md` for a full React + TypeScript example with:
- Persona sidebar
- Chat interface
- 1:1 mode
- Persistence
- Error handling

---

## Checklist

Before launching:

- [ ] API URL configured correctly
- [ ] Types match API responses
- [ ] Error handling for network failures
- [ ] Loading states implemented
- [ ] History persistence (if needed)
- [ ] Mobile responsive
- [ ] Tested with slow network (dev tools throttling)
