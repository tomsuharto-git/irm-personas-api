# Architecture

Technical architecture of the Focus Group Chat API.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLIENT (Your Site)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │   React     │  │   State     │  │  localStorage│                  │
│  │   Component │◀▶│   (history) │◀▶│  (persist)   │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        VERCEL (Serverless)                           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      FastAPI Application                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │    │
│  │  │  Endpoints  │─▶│   Engine    │─▶│  Response Generator │  │    │
│  │  │  (api.py)   │  │ (engine.py) │  │  (Claude API calls) │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │    │
│  │         │                │                    │              │    │
│  │         ▼                ▼                    ▼              │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │    │
│  │  │  Pydantic   │  │   Persona   │  │  Responder Selector │  │    │
│  │  │   Models    │  │   Loader    │  │  (AI turn-taking)   │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    audiences.json                            │    │
│  │  {                                                           │    │
│  │    "audiences": {                                            │    │
│  │      "premium_chocolate": { "personas": [...] },             │    │
│  │      "airline_travelers": { "personas": [...] }              │    │
│  │    }                                                         │    │
│  │  }                                                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        ANTHROPIC CLAUDE API                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  claude-sonnet-4-20250514                                    │    │
│  │  - Responder selection (temp 0.7)                            │    │
│  │  - Response generation (temp 0.9)                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer (`api.py`)

**Responsibility:** HTTP interface, request/response serialization

```python
# Key components
app = FastAPI()                    # Framework
CORSMiddleware                     # Cross-origin requests
Pydantic models                    # Request/response validation
Mangum handler                     # Vercel/Lambda compatibility
```

**Endpoints:**
- `GET /` - Health check
- `GET /audiences` - List available audiences
- `GET /audiences/{id}` - Get audience details
- `POST /audiences/{id}/ask` - Ask group (stateless)
- `POST /audiences/{id}/ask/{persona_id}` - Ask specific persona

**Stateless Design:**
- No server-side session storage
- Client sends full history with each request
- Server rebuilds state, processes, returns updated history

### 2. Engine Layer (`engine.py`)

**Responsibility:** Core logic, persona management, response generation

```python
class FocusGroupEngine:
    # Configuration
    client: Anthropic              # API client
    personas: List[Persona]        # Loaded personas
    category: str                  # Audience category

    # State (rebuilt per request)
    transcript: List[Dict]         # Conversation history
    persona_history: Dict[int, List[str]]  # Per-persona statements
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `load_audience()` | Load personas from JSON config |
| `_rebuild_state_from_history()` | Reconstruct state from history |
| `_select_responders()` | AI determines who responds |
| `_build_persona_prompt()` | Create system prompt with full context |
| `_generate_response()` | Get Claude response as persona |
| `ask_stateless()` | Main entry point for group questions |
| `ask_persona_stateless()` | Entry point for 1:1 questions |

### 3. Persona Data (`audiences.json`)

**Structure:**
```json
{
  "audiences": {
    "audience_id": {
      "category": "Category Name",
      "description": "Audience description",
      "personas": [
        {
          "id": 1,
          "name": "Full Name",
          "age": 28,
          "occupation": "Job Title",
          "location": "City, State",
          "backstory": "2-3 sentences about who they are",
          "category_relationship": "How they relate to the category",
          "personality_traits": ["trait1", "trait2"],
          "speech_patterns": ["pattern1", "pattern2"],
          "likely_opinions": {"topic": "opinion"}
        }
      ]
    }
  }
}
```

## Data Flow

### Request Processing

```
1. Client Request
   POST /audiences/premium_chocolate/ask
   {
     "question": "What do you think?",
     "history": [... previous messages ...]
   }

2. API Layer
   - Validate request (Pydantic)
   - Check audience exists
   - Convert history to dicts

3. Engine Layer
   a. Load audience from JSON
   b. Rebuild state from history
      - Reconstruct transcript
      - Extract per-persona history

   c. Select responders (Claude API call)
      - Build context: personas + recent speakers
      - Ask: "Who would respond to this?"
      - Parse: JSON array of names

   d. Generate responses (Claude API call per responder)
      - Build system prompt with full persona context
      - Include conversation history
      - Include persona's previous statements
      - Generate response (temp 0.9)

   e. Update transcript

4. Return Response
   {
     "responses": [...],
     "history": [... updated ...]
   }
```

### Persona Consistency Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Each Response Generation                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Build System Prompt                                          │
│     ┌──────────────────────────────────────────────────────┐    │
│     │ You ARE {name}. You are participating in a focus     │    │
│     │ group discussion.                                     │    │
│     │                                                       │    │
│     │ WHO YOU ARE:                                          │    │
│     │ - Name, Age, Occupation, Location                     │    │
│     │                                                       │    │
│     │ YOUR STORY:                                           │    │
│     │ {backstory}                                           │    │
│     │                                                       │    │
│     │ YOUR RELATIONSHIP TO {CATEGORY}:                      │    │
│     │ {category_relationship}                               │    │
│     │                                                       │    │
│     │ YOUR PERSONALITY:                                     │    │
│     │ {traits}                                              │    │
│     │                                                       │    │
│     │ HOW YOU SPEAK:                                        │    │
│     │ {speech_patterns}                                     │    │
│     │                                                       │    │
│     │ WHAT YOU'VE ALREADY SAID:    ◀── Prevents            │    │
│     │ - "Quote from earlier..."        contradictions       │    │
│     │ - "Another quote..."                                  │    │
│     │                                                       │    │
│     │ NEVER:                                                │    │
│     │ - Sound generic                                       │    │
│     │ - Contradict yourself                                 │    │
│     │ - Use survey-speak                                    │    │
│     └──────────────────────────────────────────────────────┘    │
│                                                                  │
│  2. Build User Message                                           │
│     ┌──────────────────────────────────────────────────────┐    │
│     │ [Recent conversation]                                 │    │
│     │ Moderator: Previous question                          │    │
│     │ Jennifer: Her response                                │    │
│     │ Marcus: His response                                  │    │
│     │ ---                                                   │    │
│     │ Moderator's current question: {question}              │    │
│     └──────────────────────────────────────────────────────┘    │
│                                                                  │
│  3. Claude API Call                                              │
│     model: claude-sonnet-4-20250514                              │
│     temperature: 0.9 (high variance)                             │
│     max_tokens: 300                                              │
│                                                                  │
│  4. Return Response Text                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Stateless Architecture

### Why Stateless?

| Approach | Pros | Cons |
|----------|------|------|
| **Stateful (sessions)** | Simple client code | Requires persistent storage, doesn't scale on serverless |
| **Stateless (history in request)** | Perfect for serverless, no storage needed, client controls state | Larger payloads, client complexity |

For Vercel serverless, stateless is the correct choice.

### State Reconstruction

Each request rebuilds internal state:

```python
def _rebuild_state_from_history(self, history: List[Dict]):
    # Reset
    self.transcript = history.copy()
    self.persona_history = {p.id: [] for p in self.personas}

    # Extract per-persona statements
    for msg in history:
        if msg.get("role") == "persona":
            pid = msg.get("persona_id")
            if pid in self.persona_history:
                self.persona_history[pid].append(msg.get("text", ""))
```

This ensures:
- Persona sees their previous statements
- Responder selector knows who spoke recently
- Conversation context is available

## Configuration

### Model Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Model | `claude-sonnet-4-20250514` | Balance of quality and speed |
| Response temp | 0.9 | High variance for personality |
| Selector temp | 0.7 | Balanced selection |
| Max tokens | 300 | Natural response length |

### Adjusting in `engine.py`

```python
# Response generation (line ~270)
response = self.client.messages.create(
    model="claude-sonnet-4-20250514",  # Change model here
    max_tokens=300,                     # Adjust length
    temperature=0.9,                    # Adjust variance
    ...
)

# Responder selection (line ~219)
response = self.client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=200,
    temperature=0.7,                    # Adjust selection randomness
    ...
)
```

## Error Handling

### API Layer

```python
# Audience not found
if audience_id not in config.get("audiences", {}):
    raise HTTPException(status_code=404, detail=f"Audience '{audience_id}' not found")

# Persona not found
except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

### Engine Layer

```python
# No personas loaded
if not self.personas:
    raise ValueError("No personas loaded. Call load_audience() first.")

# Persona not found
persona = next((p for p in self.personas if p.id == persona_id), None)
if not persona:
    raise ValueError(f"Persona {persona_id} not found")
```

### Client-Side

```javascript
try {
  const res = await fetch(`${API}/audiences/${audienceId}/ask`, {...});
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail);
  }
  return await res.json();
} catch (err) {
  console.error('Focus group error:', err.message);
}
```

## Performance Considerations

### Response Time Breakdown

| Step | Time | Notes |
|------|------|-------|
| API overhead | ~50ms | FastAPI routing, validation |
| State rebuild | ~5ms | In-memory operations |
| Responder selection | ~1-2s | Single Claude API call |
| Response generation | ~2-3s × N | One call per responder |
| **Total (3 responders)** | **~8-12s** | |

### Optimization Opportunities

1. **Parallel response generation** - Generate responses concurrently (not implemented)
2. **Caching responder selection** - Similar questions could reuse selections
3. **Smaller model for selection** - Use Haiku for responder selection
4. **Reduce responder count** - 2 instead of 3-4

## Security

### API Key Management

```bash
# Vercel secrets (recommended)
vercel secrets add anthropic-api-key "sk-ant-..."

# Environment variable
export ANTHROPIC_API_KEY="sk-ant-..."
```

### CORS Configuration

```python
# Current: Allow all (development)
allow_origins=["*"]

# Production: Restrict to your domain
allow_origins=["https://yourdomain.com"]
```

### Input Validation

- Pydantic models validate all inputs
- Audience IDs checked against config
- Persona IDs validated against loaded audience

## File Structure

```
focus_group/
├── api.py                 # FastAPI application
│   ├── Pydantic models    # Request/response schemas
│   ├── Endpoints          # Route handlers
│   └── Mangum handler     # Serverless compatibility
│
├── engine.py              # Core engine
│   ├── Persona class      # Data structure
│   ├── Response class     # Data structure
│   └── FocusGroupEngine   # Main logic
│       ├── load_audience()
│       ├── _rebuild_state_from_history()
│       ├── _select_responders()
│       ├── _build_persona_prompt()
│       ├── _generate_response()
│       ├── ask_stateless()
│       └── ask_persona_stateless()
│
├── audiences.json         # Persona configurations
├── requirements.txt       # Dependencies
├── vercel.json           # Deployment config
└── docs/                 # Documentation
    ├── ARCHITECTURE.md   # This file
    ├── API.md
    ├── PERSONAS.md
    ├── DEPLOYMENT.md
    └── FRONTEND.md
```
