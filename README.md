# Focus Group Chat API

A synthetic focus group system powered by IRM (Impersonas Research Model). Generate rich personas from recruitment specs and chat with them via a stateless API.

## Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Your Site     │────▶│  Focus Group    │────▶│    Claude       │
│   (Frontend)    │◀────│  API (Vercel)   │◀────│    API          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        │  Stores conversation
        │  history locally
        ▼
   [localStorage]
```

**Key Features:**
- **Stateless API** - Frontend manages conversation history (perfect for serverless)
- **Rich personas** with narrative anchors (not just demographics)
- **AI-driven turn-taking** - 2-4 personas respond naturally per question
- **Persona memory** - Prevents contradictions via history replay
- **1:1 mode** - Ask specific personas directly
- **Anti-generic safeguards** - Blocks survey-speak

---

## Quick Start

### 1. Install Dependencies

```bash
cd focus_group
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 3. Run Locally

```bash
uvicorn api:app --reload
```

API available at `http://localhost:8000`

### 4. Test with curl

```bash
# List audiences
curl http://localhost:8000/audiences

# Get audience details
curl http://localhost:8000/audiences/premium_chocolate

# Ask a question (first message - no history)
curl -X POST http://localhost:8000/audiences/premium_chocolate/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What comes to mind when you think of premium chocolate?"}'

# Ask follow-up (include history from previous response)
curl -X POST http://localhost:8000/audiences/premium_chocolate/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does that compare to grocery store chocolate?",
    "history": [
      {"role": "moderator", "text": "What comes to mind when you think of premium chocolate?"},
      {"role": "persona", "persona_id": 4, "persona_name": "Priya Sharma", "text": "My first thought is always the cacao percentage..."}
    ]
  }'
```

---

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/audiences` | List all available audiences |
| `GET` | `/audiences/{id}` | Get audience details + personas |
| `POST` | `/audiences/{id}/ask` | Ask the group (AI selects responders) |
| `POST` | `/audiences/{id}/ask/{persona_id}` | Ask specific persona (1:1) |

### Request/Response Format

**Ask Group:**
```javascript
// Request
POST /audiences/premium_chocolate/ask
{
  "question": "What makes chocolate feel premium to you?",
  "history": [...]  // Previous messages (optional for first question)
}

// Response
{
  "responses": [
    {
      "persona_id": 2,
      "persona_name": "Jennifer Martinez",
      "text": "It's that moment when you break off a piece..."
    },
    {
      "persona_id": 6,
      "persona_name": "Aisha Williams",
      "text": "For me it's about the story behind it..."
    }
  ],
  "history": [
    // Full conversation including new messages
    {"role": "moderator", "text": "What makes chocolate feel premium to you?"},
    {"role": "persona", "persona_id": 2, "persona_name": "Jennifer Martinez", "text": "..."},
    {"role": "persona", "persona_id": 6, "persona_name": "Aisha Williams", "text": "..."}
  ]
}
```

**Ask Specific Persona (1:1):**
```javascript
// Request
POST /audiences/premium_chocolate/ask/1
{
  "question": "Marcus, tell me more about your girlfriend's influence",
  "history": [...]
}

// Response
{
  "response": {
    "persona_id": 1,
    "persona_name": "Marcus Chen",
    "text": "Oh man, so she's like... she's one of those people who actually reads ingredients..."
  },
  "history": [...]  // Updated with new exchange
}
```

---

## Frontend Integration

### React Example

```typescript
// types.ts
interface Message {
  role: 'moderator' | 'persona';
  text: string;
  persona_id?: number;
  persona_name?: string;
}

interface Persona {
  id: number;
  name: string;
  age: number;
  occupation: string;
  location: string;
  backstory: string;
  personality_traits: string[];
}

// useFocusGroup.ts
const API_URL = 'https://your-api.vercel.app';

export function useFocusGroup(audienceId: string) {
  const [history, setHistory] = useState<Message[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(false);

  // Load audience on mount
  useEffect(() => {
    fetch(`${API_URL}/audiences/${audienceId}`)
      .then(r => r.json())
      .then(data => setPersonas(data.personas));
  }, [audienceId]);

  // Ask the group
  const askGroup = async (question: string) => {
    setLoading(true);
    const res = await fetch(`${API_URL}/audiences/${audienceId}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, history })
    });
    const data = await res.json();
    setHistory(data.history);  // Store updated history
    setLoading(false);
    return data.responses;
  };

  // Ask specific persona
  const askPersona = async (personaId: number, question: string) => {
    setLoading(true);
    const res = await fetch(`${API_URL}/audiences/${audienceId}/ask/${personaId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, history })
    });
    const data = await res.json();
    setHistory(data.history);
    setLoading(false);
    return data.response;
  };

  // Reset conversation
  const reset = () => setHistory([]);

  return { personas, history, loading, askGroup, askPersona, reset };
}

// FocusGroupChat.tsx
function FocusGroupChat() {
  const { personas, history, loading, askGroup, askPersona } = useFocusGroup('premium_chocolate');
  const [input, setInput] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    await askGroup(input);
    setInput('');
  };

  return (
    <div className="focus-group">
      {/* Persona sidebar */}
      <aside>
        {personas.map(p => (
          <div key={p.id} className="persona-card">
            <strong>{p.name}</strong>, {p.age}
            <p>{p.occupation}</p>
            <button onClick={() => askPersona(p.id, input)}>
              Ask directly
            </button>
          </div>
        ))}
      </aside>

      {/* Chat area */}
      <main>
        {history.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <strong>
              {msg.role === 'moderator' ? 'You' : msg.persona_name}:
            </strong>
            <p>{msg.text}</p>
          </div>
        ))}

        {loading && <div className="loading">Thinking...</div>}

        <form onSubmit={handleSubmit}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask the group..."
            disabled={loading}
          />
          <button type="submit" disabled={loading}>Send</button>
        </form>
      </main>
    </div>
  );
}
```

---

## Deploy to Vercel

### 1. Project Structure

```
focus_group/
├── api.py              # FastAPI app (entry point)
├── engine.py           # Core chat engine
├── audiences.json      # Persona configurations
├── requirements.txt    # Dependencies
├── vercel.json         # Vercel config
└── README.md
```

### 2. Deploy

```bash
cd focus_group

# Add API key as secret (one time)
vercel secrets add anthropic-api-key "sk-ant-..."

# Deploy
vercel --prod
```

### 3. Environment Variables

In Vercel Dashboard → Settings → Environment Variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key

---

## Personas

### Structure

Each persona has **narrative anchors** that enforce consistent, authentic responses:

```json
{
  "id": 1,
  "name": "Marcus Chen",
  "age": 28,
  "occupation": "Software engineer at a fintech startup",
  "location": "Austin, TX",

  "backstory": "Moved from Seattle 2 years ago. Works long hours but values work-life balance...",

  "category_relationship": "Chocolate is an impulse buy at checkout. My girlfriend introduced me to nicer brands.",

  "personality_traits": ["analytical", "skeptical of marketing", "direct communicator"],

  "speech_patterns": ["Uses tech metaphors", "Tends to qualify statements", "Self-deprecating humor"],

  "likely_opinions": {
    "premium_chocolate": "Sees value but questions if he can taste the difference"
  }
}
```

### Why Rich Personas Work

| Approach | Result |
|----------|--------|
| Demographics only | LLM predicts "mode" → everyone sounds the same |
| Rich narrative anchors | Each persona has unique perspective → real variance |

### Adding New Audiences

Edit `audiences.json` or ask Claude to generate personas from your recruitment spec:

```
"I need a focus group for [category]. Recruit:
- 2 heavy users (weekly purchase)
- 2 light users (monthly)
- 2 non-users who are aware
Mix of ages 25-55, income $50K+, urban/suburban"
```

---

## How It Works

### 1. Stateless Flow

```
Frontend                    API                         Claude
   │                         │                            │
   │─── POST /ask ──────────▶│                            │
   │    {question, history}  │                            │
   │                         │── rebuild state ──────────▶│
   │                         │   from history             │
   │                         │                            │
   │                         │── select responders ──────▶│
   │                         │   (2-4 personas)           │
   │                         │                            │
   │                         │── generate responses ─────▶│
   │                         │   (per persona)            │
   │                         │                            │
   │◀── {responses, history}─│                            │
   │                         │                            │
   │  Store history locally  │                            │
   ▼                         ▼                            ▼
```

### 2. Persona Consistency

Even though the API is stateless, personas stay consistent because:

1. **Full history replay** - Each request rebuilds what each persona has said
2. **Anti-contradiction prompt** - System prompt includes persona's previous statements
3. **Speech pattern enforcement** - Each persona has defined verbal fingerprints

### 3. Response Selection

AI determines who would naturally respond based on:
- Question topic vs persona expertise/interest
- Who hasn't spoken recently
- Natural group dynamics (some people talk more)
- Previous statements that relate to this question

---

## Configuration

### Models & Parameters

| Setting | Value | Purpose |
|---------|-------|---------|
| Response model | `claude-sonnet-4-20250514` | Quality + speed balance |
| Response temperature | 0.9 | High personality variance |
| Selector temperature | 0.7 | Balanced turn-taking |
| Max response tokens | 300 | Natural response length |

### Customization

Edit `engine.py` to change:
- Model selection
- Temperature settings
- Response length limits
- Prompt templates

---

## Files

| File | Description |
|------|-------------|
| `api.py` | Stateless FastAPI endpoints (~150 lines) |
| `engine.py` | Core chat engine with persona management (~420 lines) |
| `audiences.json` | Persona configurations |
| `requirements.txt` | Python dependencies |
| `vercel.json` | Vercel deployment config |

---

## Example Audience: Premium Chocolate

6 personas with distinct voices:

| Persona | Profile | Voice |
|---------|---------|-------|
| **Marcus Chen** | 28, software engineer, Austin | Tech metaphors, skeptical, girlfriend-influenced |
| **Jennifer Martinez** | 42, teacher, Columbus | Sensory descriptions, evening ritual, nurturing |
| **David Thompson** | 58, retired, Scottsdale | Brief, pragmatic, references late wife |
| **Priya Sharma** | 35, consultant, Chicago | Data-driven, health-conscious, self-aware |
| **Bobby DiNardo** | 47, contractor, Providence | Family-focused, Italian traditions, direct |
| **Aisha Williams** | 31, nonprofit, Atlanta | Story-driven, social media savvy, ethical |

---

## Limitations

- **Response time**: 3-8 seconds per question (Claude API latency × responders)
- **History size**: Very long conversations may hit token limits (~50+ exchanges)
- **Cold starts**: First request after inactivity may be slower on Vercel

---

## Troubleshooting

**"Audience not found"**
- Check `audiences.json` has your audience ID
- Audience IDs are case-sensitive

**Personas sound similar**
- Ensure personas have distinct `backstory` and `category_relationship`
- Check `personality_traits` and `speech_patterns` are different

**API timeout**
- Vercel functions have 10s default timeout
- Upgrade to Pro for longer timeouts, or reduce responder count

---

## Documentation

Detailed guides in the `docs/` folder:

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, data flow, component details |
| [API.md](docs/API.md) | Complete API reference with examples |
| [PERSONAS.md](docs/PERSONAS.md) | How to create rich, distinct personas |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deploy to Vercel step-by-step |
| [FRONTEND.md](docs/FRONTEND.md) | React hooks, TypeScript types, UI patterns |

---

## Support

Built on IRM (Impersonas Research Model) methodology.

For new audience generation or issues, work with Claude Code.
