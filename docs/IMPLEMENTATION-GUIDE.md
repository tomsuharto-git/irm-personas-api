# Focus Group Chat API - Implementation Guide

## Overview

This is a **stateless synthetic focus group API** that enables conversations with AI-powered personas. Each persona has rich backstory, personality traits, and speech patterns that ensure consistent, authentic responses.

**Production URL:** `https://focusgroup-plum.vercel.app`
**GitHub:** `https://github.com/tomsuharto-git/irm-personas-api`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Your Website                          │
│   (React/Next.js frontend that manages conversation state)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP POST with history
┌─────────────────────────────────────────────────────────────┐
│                    Vercel Serverless API                     │
│                  focusgroup-plum.vercel.app                  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │ api/index.py│  │  engine.py   │  │  audiences.json   │   │
│  │  (routing)  │  │ (AI logic)   │  │  (persona data)   │   │
│  └─────────────┘  └──────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ Claude API calls
┌─────────────────────────────────────────────────────────────┐
│                     Anthropic Claude API                     │
│         (generates persona responses + selects speakers)     │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Stateless API**: Client manages conversation history. Each request includes full history, API returns updated history. No server-side session storage.

2. **AI-Driven Turn Taking**: When you ask the group a question, Claude analyzes the question + personas and selects 2-4 who would naturally respond (not everyone every time).

3. **Rich Persona Anchors**: Each persona has backstory, category relationship, personality traits, and speech patterns that get injected into every prompt to ensure consistency.

4. **Vercel api/ Directory Format**: Uses the modern Vercel Python serverless format with `api/index.py` using `BaseHTTPRequestHandler`.

---

## File Structure

```
focus_group/
├── api/
│   └── index.py           # Vercel serverless handler (routing + CORS)
├── docs/
│   └── IMPLEMENTATION-GUIDE.md  # This file
├── personas/              # Generated persona images
│   ├── derek_kowalski.png
│   ├── marcus_reeves.png
│   └── jasmine_okonkwo.png
├── audiences.json         # All audience + persona definitions
├── engine.py              # Core FocusGroupEngine class
├── api.py                 # Original FastAPI version (legacy, not used by Vercel)
├── requirements.txt       # Python dependencies
├── vercel.json            # Vercel deployment config
└── .gitignore
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/audiences` | List all audiences with persona counts |
| GET | `/audiences/{id}` | Get full audience details including all personas |
| POST | `/audiences/{id}/ask` | Ask the group (AI picks 2-4 responders) |
| POST | `/audiences/{id}/ask/{persona_id}` | Ask specific persona (1:1 mode) |

### Request/Response Examples

**Ask Group:**
```json
// POST /audiences/xrp_army/ask
// Request:
{
  "question": "How did you first discover XRP?",
  "history": []
}

// Response:
{
  "responses": [
    {"persona_id": 1, "persona_name": "Derek Kowalski", "text": "My brother-in-law..."},
    {"persona_id": 3, "persona_name": "Jasmine Okonkwo", "text": "I discovered it through..."}
  ],
  "history": [
    {"role": "moderator", "text": "How did you first discover XRP?"},
    {"role": "persona", "persona_id": 1, "persona_name": "Derek Kowalski", "text": "My brother-in-law..."},
    {"role": "persona", "persona_id": 3, "persona_name": "Jasmine Okonkwo", "text": "I discovered it through..."}
  ]
}
```

**Ask Specific Persona:**
```json
// POST /audiences/xrp_army/ask/1
// Request:
{
  "question": "Tell me more about your brother-in-law",
  "history": [/* previous messages */]
}

// Response:
{
  "response": {"persona_id": 1, "persona_name": "Derek Kowalski", "text": "..."},
  "history": [/* updated history */]
}
```

---

## How to Add a New Audience

### Step 1: Research the Audience

Before creating personas, gather detailed information about the target audience:
- Who are they? Demographics, psychographics
- What language/terminology do they use?
- What are their common opinions, concerns, motivations?
- What makes them distinct from general population?

### Step 2: Define Personas in audiences.json

Add a new entry to `audiences.json`:

```json
{
  "audiences": {
    "your_audience_id": {
      "category": "Category Name",
      "description": "Brief description of who this audience represents",
      "personas": [
        {
          "id": 1,
          "name": "Full Name",
          "age": 35,
          "occupation": "Job title and employer type",
          "location": "City, State",
          "image": "personas/filename.png",

          "backstory": "2-3 sentences of personal history that explains HOW they came to be part of this audience. Include specific details like timeline, family influences, pivotal moments.",

          "category_relationship": "Their specific relationship to the category/topic. Not generic - specific to THIS person. What's their history? Current behavior? Emotional connection?",

          "personality_traits": [
            "trait that affects how they communicate",
            "trait that affects their opinions",
            "trait that makes them distinct from others"
          ],

          "speech_patterns": [
            "Specific verbal habit or phrase style",
            "How they structure responses",
            "Unique linguistic markers"
          ],

          "likely_opinions": {
            "topic_1": "Their specific stance and why",
            "topic_2": "Another opinion with reasoning"
          }
        }
      ]
    }
  }
}
```

### Step 3: Generate Persona Images

Use the GPT-Image-1.5 image generator:

```bash
# From any Claude Code session with /image-creator skill:
# Request photorealistic portrait with specific details:

"Create a photorealistic portrait of [Name]: [age]-year-old [ethnicity] [gender],
[occupation] from [location]. [Physical description: build, hair, facial features].
Wearing [clothing appropriate to their role]. [Expression that matches personality].
Natural lighting, professional headshot style."
```

Save images to `focus_group/personas/` directory.

### Step 4: Test Locally

```bash
cd focus_group
python -c "
from engine import FocusGroupEngine
engine = FocusGroupEngine()
result = engine.ask_stateless(
    question='Test question for your audience',
    audience_id='your_audience_id',
    config_path='audiences.json'
)
for r in result['responses']:
    print(f\"{r['persona_name']}: {r['text']}\n\")
"
```

### Step 5: Deploy

```bash
git add -A
git commit -m "Add [audience name] audience with [N] personas"
git push tomsuharto-git main
vercel --prod --yes
```

---

## Persona Design Best Practices

### What Makes Personas Feel Real

1. **Specific Backstory**: Not "got interested in crypto" but "brother-in-law wouldn't shut up about Bitcoin at Thanksgiving 2017"

2. **Consistent Voice**: Each persona should have distinct speech patterns:
   - Derek: Uses hashtags, tech metaphors despite being blue collar, confrontational
   - Marcus: Analytical, qualifies statements, references data
   - Jasmine: Legal terminology, community-focused, measured but passionate

3. **Grounded Opinions**: Opinions should stem from their backstory, not be generic. Derek's skepticism of Bitcoin comes from his brother-in-law's Bitcoin evangelism.

4. **Category Relationship**: How do they ACTUALLY interact with the topic? Not "interested in XRP" but "checks price daily, participates in Twitter spaces, filed Deaton affidavit"

### Anti-Generic Safeguards

The engine prompt explicitly blocks:
- "I think..." as default opener (vary: "Honestly," "Look," "For me,")
- Generic phrases: "quality matters to me", "it depends"
- Survey-speak: "I would say that...", "In my opinion..."
- Perfect grammar if it doesn't fit the character

### Voice Differentiation Table

| Persona Type | Speech Markers |
|--------------|----------------|
| Blue collar | Shorter sentences, slang, direct, analogies to their work |
| Professional | Complete sentences, industry jargon, data references |
| Legal/academic | Precise language, qualifications, cites sources |
| Community member | In-group terminology, references shared experiences |

---

## Engine Technical Details

### FocusGroupEngine Class

```python
class FocusGroupEngine:
    def __init__(self, api_key: str = None)

    # Load personas from config
    def load_audience(self, audience_id: str, config_path: str)

    # AI selects which personas respond
    def _select_responders(self, question: str) -> List[int]

    # Generate response for one persona
    def _generate_response(self, persona: Persona, question: str) -> str

    # Main stateless entry point
    def ask_stateless(self, question, audience_id, history, config_path) -> dict

    # Ask specific persona (1:1 mode)
    def ask_persona_stateless(self, persona_id, question, audience_id, history, config_path) -> dict
```

### Response Selection Logic

When `ask_stateless` is called:

1. Claude receives list of all personas with their details
2. Claude analyzes the question topic
3. Claude selects 2-4 personas based on:
   - Relevance to their backstory/expertise
   - Who hasn't spoken recently (from history)
   - Natural group dynamics (some people talk more)
4. Each selected persona generates their response with full context

### System Prompt Structure

Each persona response uses this prompt structure:

```
You are {name}, a {age}-year-old {occupation} from {location}.

YOUR STORY:
{backstory}

YOUR RELATIONSHIP TO {category}:
{category_relationship}

PERSONALITY: {traits joined}

SPEECH PATTERNS: {patterns joined}

CONVERSATION SO FAR:
{formatted history}

YOUR PREVIOUS STATEMENTS IN THIS CONVERSATION:
{what this persona has already said}

---
Respond naturally to: "{question}"

RULES:
- Stay in character
- Reference your backstory when relevant
- Use your speech patterns
- Don't contradict what you've already said
- 2-4 sentences typical
```

---

## Deployment Details

### Vercel Configuration

**vercel.json:**
```json
{
  "version": 2,
  "rewrites": [
    { "source": "/(.*)", "destination": "/api" }
  ]
}
```

The `api/index.py` file uses Python's `BaseHTTPRequestHandler` (not FastAPI) because:
- Vercel's api/ directory auto-detects Python handlers
- No need for Mangum adapter
- Simpler deployment, fewer dependencies at runtime

### Environment Variables

Required on Vercel:
- `ANTHROPIC_API_KEY`: Your Anthropic API key (no trailing newlines!)

To set:
```bash
vercel env add ANTHROPIC_API_KEY production <<< "$(echo -n "$ANTHROPIC_API_KEY")"
```

### Deployment Commands

```bash
# Deploy to production
cd focus_group
vercel --prod --yes

# Check logs
vercel logs focusgroup-plum.vercel.app

# View deployment details
vercel inspect focusgroup-plum.vercel.app
```

---

## Troubleshooting

### "FUNCTION_INVOCATION_FAILED"

Check Vercel logs for actual error. Common causes:
- Missing environment variable
- Import errors (relative imports don't work)
- API key has newline character

### "Illegal header value" error

The API key has a newline. Re-add it:
```bash
vercel env rm ANTHROPIC_API_KEY production --yes
vercel env add ANTHROPIC_API_KEY production <<< "$(echo -n "$ANTHROPIC_API_KEY")"
vercel --prod --yes
```

### Personas sound too similar

Review their `speech_patterns` and `personality_traits`. Make sure:
- Each has distinct verbal habits
- Backstories create different perspectives
- `likely_opinions` are specific, not generic

### Response times slow

Claude API calls take 5-15 seconds. For group questions, multiple personas respond sequentially. Consider:
- Reducing max responders (edit `_select_responders`)
- Using streaming (requires code changes)

---

## Current Audiences

### xrp_army
XRP/Ripple community members who supported XRP through the SEC lawsuit.

| Persona | Demographics | Key Traits |
|---------|--------------|------------|
| Derek Kowalski | 41, HVAC owner, Phoenix | OG since 2017, tribal, uses hashtags |
| Marcus Reeves | 34, Financial analyst, Charlotte | Analytical, traditional finance background |
| Jasmine Okonkwo | 29, Paralegal, Atlanta | Legal-minded, community organizer |

### premium_chocolate
US consumers interested in premium chocolate (indulgers, gift-buyers, health-conscious).

6 personas with varying relationships to chocolate consumption.

---

## Future Enhancements

- [ ] Streaming responses for better UX
- [ ] Persona image serving from Vercel (currently GitHub raw)
- [ ] Analytics/logging for conversation quality
- [ ] Batch persona generation from recruitment spec
- [ ] Export transcripts for analysis
