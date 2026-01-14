# Adding a New Audience - Quick Reference

## Prerequisites
- Anthropic API key set in environment
- Access to GPT-Image-1.5 for persona images

---

## Step-by-Step Process

### 1. Research Your Audience

Before writing personas, understand:
- **Who they are**: Demographics, psychographics, lifestyle
- **Their language**: Terminology, slang, in-group phrases
- **Their opinions**: Common views, controversies, tribal allegiances
- **Their journey**: How do people become part of this group?

**Example research prompt:**
```
Research the [audience name] community. I need to understand:
1. Demographics (age range, gender split, geography, income)
2. Psychographics (values, motivations, fears)
3. Language/terminology they use
4. Common opinions and debates within the community
5. How someone typically becomes part of this group
```

---

### 2. Design 3-6 Personas

Each persona needs:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Unique integer | 1, 2, 3 |
| `name` | Full realistic name | "Derek Kowalski" |
| `age` | Specific age | 41 |
| `occupation` | Job + employer type | "HVAC technician, owns small business" |
| `location` | City, State | "Phoenix, AZ" |
| `backstory` | HOW they joined this audience (2-3 sentences with specific details) | "Got into crypto in 2017 after his brother-in-law..." |
| `category_relationship` | Their CURRENT relationship to the topic | "Checks price daily, filed Deaton affidavit..." |
| `personality_traits` | 3-5 traits affecting communication | ["tribal loyalty", "aggressive defender", "skeptical of institutions"] |
| `speech_patterns` | How they talk distinctly | ["Uses hashtags in conversation", "Tech metaphors despite blue collar"] |
| `likely_opinions` | Specific stances on key topics | {"bitcoin": "Dismissive - sees it as inferior...", "sec_lawsuit": "Deeply personal..."} |

**Diversity checklist:**
- [ ] Mix of ages
- [ ] Gender balance (unless audience is skewed)
- [ ] Different entry points to the community
- [ ] Varying levels of engagement
- [ ] Different communication styles

---

### 3. Add to audiences.json

```json
{
  "audiences": {
    "existing_audience": { ... },

    "your_new_audience": {
      "category": "Display Name for Category",
      "description": "One sentence describing who this audience represents",
      "personas": [
        {
          "id": 1,
          "name": "First Last",
          "age": 35,
          "occupation": "Job title, employer type",
          "location": "City, State",
          "image": "personas/first_last.png",
          "backstory": "Specific story of how they became part of this audience...",
          "category_relationship": "Their current engagement with the topic...",
          "personality_traits": ["trait1", "trait2", "trait3"],
          "speech_patterns": ["pattern1", "pattern2"],
          "likely_opinions": {
            "key_topic_1": "Their specific view and why",
            "key_topic_2": "Another opinion"
          }
        }
        // ... more personas
      ]
    }
  }
}
```

---

### 4. Generate Persona Images

Use GPT-Image-1.5 with detailed prompts:

```
Create a photorealistic portrait of [Full Name]:
- [Age]-year-old [ethnicity] [gender]
- [Occupation] from [Location]
- Physical: [build], [hair color/style], [facial features]
- Wearing: [clothing appropriate to their role/personality]
- Expression: [matches their personality - confident, thoughtful, warm, etc.]
- Style: Natural lighting, professional headshot, neutral background
```

**Save to:** `focus_group/personas/firstname_lastname.png`

**Image URL pattern:**
```
https://raw.githubusercontent.com/tomsuharto-git/irm-personas-api/main/personas/firstname_lastname.png
```

---

### 5. Test Locally

```bash
cd "/Users/tomsuharto/Documents/Obsidian Vault/Claude Code/Synthetic Panels/focus_group"

python3 -c "
from engine import FocusGroupEngine

engine = FocusGroupEngine()
result = engine.ask_stateless(
    question='[Test question relevant to your audience]',
    audience_id='your_new_audience',
    config_path='audiences.json'
)

print('=== RESPONSES ===')
for r in result['responses']:
    print(f\"\\n{r['persona_name']}:\")
    print(r['text'])
"
```

**What to check:**
- [ ] All personas can be loaded (no JSON errors)
- [ ] Responses reflect persona personalities
- [ ] Speech patterns are distinct
- [ ] No generic survey-speak

---

### 6. Deploy

```bash
# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "Add [audience_name] audience with [N] personas

- [Persona 1 name]: [brief description]
- [Persona 2 name]: [brief description]
- [Persona 3 name]: [brief description]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Push to GitHub
git push tomsuharto-git main

# Deploy to Vercel
vercel --prod --yes
```

---

### 7. Verify Deployment

```bash
# Check audience appears in list
curl -s https://focusgroup-plum.vercel.app/audiences | jq .

# Get full audience details
curl -s https://focusgroup-plum.vercel.app/audiences/your_new_audience | jq .

# Test asking a question
curl -s -X POST 'https://focusgroup-plum.vercel.app/audiences/your_new_audience/ask' \
  -H 'Content-Type: application/json' \
  -d '{"question": "Test question here"}'
```

---

## Persona Quality Checklist

Before deploying, verify each persona:

**Backstory:**
- [ ] Specific (dates, names, places)
- [ ] Explains HOW they joined the audience
- [ ] Creates foundation for their opinions

**Category Relationship:**
- [ ] Current, not historical
- [ ] Specific behaviors (not just "interested in")
- [ ] Emotional connection clear

**Personality Traits:**
- [ ] Affect how they communicate
- [ ] Distinct from other personas
- [ ] Create predictable response patterns

**Speech Patterns:**
- [ ] Unique verbal habits
- [ ] Would sound different in a transcript
- [ ] Match their background (education, region, profession)

**Likely Opinions:**
- [ ] Specific stances, not "it depends"
- [ ] Stem from their backstory
- [ ] Cover key topics for this audience

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Generic backstory: "Became interested in X" | Add specific trigger: "Saw a YouTube video in March 2021 that..." |
| Similar speech patterns | Vary: one uses questions, one uses analogies, one is blunt |
| Professional persona sounds casual | Add formal markers: complete sentences, industry jargon |
| Opinions don't connect to backstory | Revise backstory to explain WHY they hold these views |
| All personas same age range | Spread ages to get generational perspectives |

---

## Template: Persona JSON

```json
{
  "id": 1,
  "name": "",
  "age": 0,
  "occupation": "",
  "location": "",
  "image": "personas/.png",
  "backstory": "",
  "category_relationship": "",
  "personality_traits": [],
  "speech_patterns": [],
  "likely_opinions": {}
}
```
