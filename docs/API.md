# API Reference

Complete API specification for the Focus Group Chat API.

## Base URL

```
Local:      http://localhost:8000
Production: https://your-app.vercel.app
```

## Authentication

The API itself is public. The Anthropic API key is configured server-side.

For production, consider adding:
- API key authentication
- Rate limiting
- Request signing

---

## Endpoints

### Health Check

```
GET /
```

**Response:**
```json
{
  "status": "ok",
  "service": "focus-group-api",
  "version": "2.0.0",
  "mode": "stateless"
}
```

---

### List Audiences

```
GET /audiences
```

Returns all available audiences.

**Response:**
```json
{
  "audiences": [
    {
      "id": "premium_chocolate",
      "category": "Premium Chocolate",
      "description": "US consumers interested in premium chocolate",
      "persona_count": 6
    },
    {
      "id": "airline_travelers",
      "category": "International Air Travel",
      "description": "Premium leisure travelers",
      "persona_count": 8
    }
  ]
}
```

---

### Get Audience Details

```
GET /audiences/{audience_id}
```

Returns full details including all personas.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `audience_id` | string | Unique audience identifier |

**Response:**
```json
{
  "id": "premium_chocolate",
  "category": "Premium Chocolate",
  "personas": [
    {
      "id": 1,
      "name": "Marcus Chen",
      "age": 28,
      "occupation": "Software engineer at a fintech startup",
      "location": "Austin, TX",
      "backstory": "Moved from Seattle 2 years ago. Works long hours but values work-life balance on weekends...",
      "personality_traits": ["analytical", "skeptical of marketing", "direct communicator"]
    },
    {
      "id": 2,
      "name": "Jennifer Martinez",
      "age": 42,
      "occupation": "Middle school English teacher",
      "location": "Columbus, OH",
      "backstory": "Single mom of two teenagers. Teaching for 18 years...",
      "personality_traits": ["nurturing", "appreciates small luxuries", "articulate"]
    }
  ]
}
```

**Errors:**
| Status | Description |
|--------|-------------|
| 404 | Audience not found |

---

### Ask Group (Main Endpoint)

```
POST /audiences/{audience_id}/ask
```

Ask the focus group a question. AI selects 2-4 personas who would naturally respond.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `audience_id` | string | Unique audience identifier |

**Request Body:**
```json
{
  "question": "What comes to mind when you think of premium chocolate?",
  "history": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | The moderator's question |
| `history` | array | No | Previous conversation messages (empty for first question) |

**History Message Format:**
```json
{
  "role": "moderator" | "persona",
  "text": "Message content",
  "persona_id": 1,           // Only for persona messages
  "persona_name": "Marcus"   // Only for persona messages
}
```

**Response:**
```json
{
  "responses": [
    {
      "persona_id": 4,
      "persona_name": "Priya Sharma",
      "text": "Honestly? My first thought is always the cacao percentage..."
    },
    {
      "persona_id": 2,
      "persona_name": "Jennifer Martinez",
      "text": "It's that moment when you break off a piece and it makes that perfect *snap*..."
    },
    {
      "persona_id": 6,
      "persona_name": "Aisha Williams",
      "text": "For me it's about the story behind it..."
    }
  ],
  "history": [
    {
      "role": "moderator",
      "text": "What comes to mind when you think of premium chocolate?",
      "persona_id": null,
      "persona_name": null
    },
    {
      "role": "persona",
      "text": "Honestly? My first thought is always the cacao percentage...",
      "persona_id": 4,
      "persona_name": "Priya Sharma"
    },
    {
      "role": "persona",
      "text": "It's that moment when you break off a piece and it makes that perfect *snap*...",
      "persona_id": 2,
      "persona_name": "Jennifer Martinez"
    },
    {
      "role": "persona",
      "text": "For me it's about the story behind it...",
      "persona_id": 6,
      "persona_name": "Aisha Williams"
    }
  ]
}
```

**Errors:**
| Status | Description |
|--------|-------------|
| 404 | Audience not found |
| 422 | Validation error (invalid request body) |

---

### Ask Specific Persona (1:1 Mode)

```
POST /audiences/{audience_id}/ask/{persona_id}
```

Ask a specific persona directly.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `audience_id` | string | Unique audience identifier |
| `persona_id` | integer | Persona ID to address |

**Request Body:**
```json
{
  "question": "Tell me more about your girlfriend's influence",
  "history": [...]
}
```

**Response:**
```json
{
  "response": {
    "persona_id": 1,
    "persona_name": "Marcus Chen",
    "text": "Oh man, so she's like... she's one of those people who actually reads the ingredients on everything..."
  },
  "history": [...]
}
```

**Errors:**
| Status | Description |
|--------|-------------|
| 404 | Audience or persona not found |
| 422 | Validation error |

---

## Usage Examples

### cURL

**First question (no history):**
```bash
curl -X POST https://your-api.vercel.app/audiences/premium_chocolate/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What comes to mind when you think of premium chocolate?"
  }'
```

**Follow-up question (with history):**
```bash
curl -X POST https://your-api.vercel.app/audiences/premium_chocolate/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does that compare to grocery store chocolate?",
    "history": [
      {"role": "moderator", "text": "What comes to mind when you think of premium chocolate?"},
      {"role": "persona", "persona_id": 4, "persona_name": "Priya Sharma", "text": "My first thought is always the cacao percentage..."},
      {"role": "persona", "persona_id": 2, "persona_name": "Jennifer Martinez", "text": "It'\''s that moment when you break off a piece..."}
    ]
  }'
```

**Direct question to specific persona:**
```bash
curl -X POST https://your-api.vercel.app/audiences/premium_chocolate/ask/1 \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Marcus, tell me more about that",
    "history": [...]
  }'
```

### JavaScript (fetch)

```javascript
const API_URL = 'https://your-api.vercel.app';

// First question
async function startConversation(audienceId, question) {
  const response = await fetch(`${API_URL}/audiences/${audienceId}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  return response.json();
}

// Follow-up with history
async function askFollowUp(audienceId, question, history) {
  const response = await fetch(`${API_URL}/audiences/${audienceId}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history })
  });
  return response.json();
}

// Ask specific persona
async function askPersona(audienceId, personaId, question, history) {
  const response = await fetch(`${API_URL}/audiences/${audienceId}/ask/${personaId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history })
  });
  return response.json();
}

// Usage
let history = [];

// First question
const result1 = await startConversation('premium_chocolate', 'What do you think of premium chocolate?');
history = result1.history;
console.log('Responses:', result1.responses);

// Follow-up
const result2 = await askFollowUp('premium_chocolate', 'How does that compare to regular chocolate?', history);
history = result2.history;
console.log('Responses:', result2.responses);

// Direct question
const result3 = await askPersona('premium_chocolate', 1, 'Tell me more about that', history);
history = result3.history;
console.log('Response:', result3.response);
```

### Python (requests)

```python
import requests

API_URL = 'https://your-api.vercel.app'

def ask_group(audience_id: str, question: str, history: list = None):
    response = requests.post(
        f'{API_URL}/audiences/{audience_id}/ask',
        json={'question': question, 'history': history or []}
    )
    return response.json()

def ask_persona(audience_id: str, persona_id: int, question: str, history: list):
    response = requests.post(
        f'{API_URL}/audiences/{audience_id}/ask/{persona_id}',
        json={'question': question, 'history': history}
    )
    return response.json()

# Usage
history = []

# First question
result = ask_group('premium_chocolate', 'What comes to mind when you think of premium chocolate?')
history = result['history']
for r in result['responses']:
    print(f"{r['persona_name']}: {r['text']}")

# Follow-up
result = ask_group('premium_chocolate', 'How does that compare to grocery store chocolate?', history)
history = result['history']

# Direct question
result = ask_persona('premium_chocolate', 1, 'Tell me more', history)
print(f"{result['response']['persona_name']}: {result['response']['text']}")
```

---

## Response Behavior

### Responder Selection

The AI selects 2-4 personas based on:
- Question topic relevance to persona expertise/interests
- Who hasn't spoken recently
- Natural group dynamics
- Previous statements that relate to the question

### Response Characteristics

- **Length:** Typically 2-4 sentences (varies naturally)
- **Tone:** Matches persona's speech patterns
- **Consistency:** Doesn't contradict previous statements
- **Authenticity:** Avoids survey-speak and generic phrases

---

## Rate Limits

No built-in rate limiting. Consider adding for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/audiences/{audience_id}/ask")
@limiter.limit("10/minute")
async def ask_group(request: Request, ...):
    ...
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

### Common Errors

| Status | Cause | Solution |
|--------|-------|----------|
| 404 | Audience not found | Check audience ID against `/audiences` |
| 404 | Persona not found | Check persona ID against `/audiences/{id}` |
| 422 | Invalid request body | Check request matches schema |
| 500 | Claude API error | Check API key, retry |
| 504 | Timeout | Reduce responder count, upgrade Vercel plan |

---

## OpenAPI Schema

Available at:
```
GET /openapi.json
GET /docs        # Swagger UI
GET /redoc       # ReDoc
```
