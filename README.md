# Focus Group Chat API

Stateless API for synthetic focus group conversations with AI-powered personas.

**Production URL:** https://focusgroup-plum.vercel.app
**GitHub:** https://github.com/tomsuharto-git/irm-personas-api

---

## Quick Start

```bash
# List audiences
curl https://focusgroup-plum.vercel.app/audiences

# Get persona details
curl https://focusgroup-plum.vercel.app/audiences/xrp_army

# Ask the group
curl -X POST 'https://focusgroup-plum.vercel.app/audiences/xrp_army/ask' \
  -H 'Content-Type: application/json' \
  -d '{"question": "How did you first discover XRP?"}'
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| **[Implementation Guide](docs/IMPLEMENTATION-GUIDE.md)** | Full technical documentation, architecture, engine details |
| **[Adding New Audiences](docs/ADDING-NEW-AUDIENCE.md)** | Step-by-step guide for creating personas |

---

## Current Audiences

| ID | Category | Personas |
|----|----------|----------|
| `xrp_army` | XRP/Ripple Community | Derek (41), Marcus (34), Jasmine (29) |
| `premium_chocolate` | Premium Chocolate Consumers | 6 personas |

### XRP Army Personas

| Name | Age | Role | Key Traits |
|------|-----|------|------------|
| Derek Kowalski | 41 | HVAC business owner, Phoenix | OG since 2017, tribal, uses #XRPTheStandard |
| Marcus Reeves | 34 | Financial analyst, Charlotte | Analytical, traditional finance background |
| Jasmine Okonkwo | 29 | Paralegal, Atlanta | Legal-minded, community organizer |

**Persona Images:**
```
https://raw.githubusercontent.com/tomsuharto-git/irm-personas-api/main/personas/derek_kowalski.png
https://raw.githubusercontent.com/tomsuharto-git/irm-personas-api/main/personas/marcus_reeves.png
https://raw.githubusercontent.com/tomsuharto-git/irm-personas-api/main/personas/jasmine_okonkwo.png
```

---

## How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Your Site     │────▶│  Focus Group    │────▶│    Claude       │
│   (Frontend)    │◀────│  API (Vercel)   │◀────│    API          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        │  Stores conversation
        │  history locally
        ▼
   [State/localStorage]
```

**Key Features:**
- **Stateless API** - Frontend manages conversation history
- **Rich personas** with backstory, personality, speech patterns
- **AI-driven turn-taking** - 2-4 personas respond naturally per question
- **Persona memory** - History replay prevents contradictions
- **1:1 mode** - Ask specific personas directly

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/audiences` | List all audiences |
| `GET` | `/audiences/{id}` | Get audience + personas |
| `POST` | `/audiences/{id}/ask` | Ask group (AI picks responders) |
| `POST` | `/audiences/{id}/ask/{persona_id}` | Ask specific persona (1:1) |

### Request/Response Format

**Ask Group:**
```json
// POST /audiences/xrp_army/ask
{
  "question": "What do you think about the SEC lawsuit outcome?",
  "history": []
}

// Response:
{
  "responses": [
    {"persona_id": 1, "persona_name": "Derek Kowalski", "text": "..."},
    {"persona_id": 3, "persona_name": "Jasmine Okonkwo", "text": "..."}
  ],
  "history": [
    {"role": "moderator", "text": "What do you think..."},
    {"role": "persona", "persona_id": 1, "persona_name": "Derek Kowalski", "text": "..."},
    {"role": "persona", "persona_id": 3, "persona_name": "Jasmine Okonkwo", "text": "..."}
  ]
}
```

**Ask Specific Persona:**
```json
// POST /audiences/xrp_army/ask/1
{
  "question": "Tell me more about your brother-in-law",
  "history": [/* previous messages */]
}

// Response:
{
  "response": {"persona_id": 1, "persona_name": "Derek Kowalski", "text": "..."},
  "history": [/* updated */]
}
```

---

## TypeScript Types

```typescript
interface Persona {
  id: number;
  name: string;
  age: number;
  occupation: string;
  location: string;
  backstory: string;
  personality_traits: string[];
  image?: string;
}

interface Message {
  role: "moderator" | "persona";
  text: string;
  persona_id?: number;
  persona_name?: string;
}

interface AskRequest {
  question: string;
  history?: Message[];
}

interface AskResponse {
  responses: Array<{
    persona_id: number;
    persona_name: string;
    text: string;
  }>;
  history: Message[];
}
```

---

## Local Development

```bash
cd focus_group
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"

# Test with Python
python3 -c "
from engine import FocusGroupEngine
engine = FocusGroupEngine()
result = engine.ask_stateless(
    question='How did you first discover XRP?',
    audience_id='xrp_army',
    config_path='audiences.json'
)
for r in result['responses']:
    print(f\"{r['persona_name']}: {r['text']}\n\")
"
```

---

## Deploy

```bash
git add -A
git commit -m "Your changes"
git push tomsuharto-git main
vercel --prod --yes
```

---

## File Structure

```
focus_group/
├── api/
│   └── index.py           # Vercel serverless handler
├── docs/
│   ├── IMPLEMENTATION-GUIDE.md
│   └── ADDING-NEW-AUDIENCE.md
├── personas/              # Generated persona images
│   ├── derek_kowalski.png
│   ├── marcus_reeves.png
│   └── jasmine_okonkwo.png
├── audiences.json         # Audience + persona definitions
├── engine.py              # Core FocusGroupEngine class
├── requirements.txt       # Python dependencies
└── vercel.json            # Vercel config
```

---

## Tech Stack

- **Runtime:** Vercel Serverless (Python 3.12)
- **AI:** Anthropic Claude API
- **Persona Images:** GPT-Image-1.5

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `FUNCTION_INVOCATION_FAILED` | Check Vercel logs: `vercel logs focusgroup-plum.vercel.app` |
| API key error | Re-add without newlines: `vercel env add ANTHROPIC_API_KEY production <<< "$(echo -n "$ANTHROPIC_API_KEY")"` |
| Personas sound similar | Review `speech_patterns` and `personality_traits` in audiences.json |
| Slow responses | Claude API takes 5-15s for multi-persona responses |

---

Built on IRM (Impersonas Research Model) methodology.
