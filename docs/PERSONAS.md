# Persona Creation Guide

How to create rich, consistent personas for focus group research.

## Why Rich Personas Matter

The #1 problem with synthetic research: **everyone sounds the same**.

This happens because LLMs predict the "mode" (most likely response). When you just provide demographics, you get modal responses.

**Demographics only:**
```
Profile: 35-year-old male, tech worker, high income
Response: "I value quality and am willing to pay more for premium products."

Profile: 28-year-old male, tech worker, high income
Response: "I value quality and am willing to pay more for premium products."
```

**Rich personas:**
```
Marcus Chen, 28, software engineer: "Honestly? I can't taste the difference
between fancy chocolate and Hershey's. My girlfriend keeps trying to educate
my palate but I'm a lost cause."

David Chen, 35, product manager: "After my promotion, I started treating myself
to better things. It started with coffee, then wine, now chocolate. It's become
part of how I decompress."
```

Same demographics, different narratives → different responses.

---

## Persona Structure

### Required Fields

```json
{
  "id": 1,
  "name": "Marcus Chen",
  "age": 28,
  "occupation": "Software engineer at a fintech startup",
  "location": "Austin, TX",
  "backstory": "Moved from Seattle 2 years ago for a job opportunity. Works long hours but values work-life balance on weekends. Grew up in a household where food was fuel, not experience.",
  "category_relationship": "Chocolate is an impulse buy at checkout for me. Never seek it out specifically. My girlfriend introduced me to nicer brands last year.",
  "personality_traits": ["analytical", "skeptical of marketing claims", "direct communicator"],
  "speech_patterns": ["Uses tech metaphors", "Tends to qualify statements", "Self-deprecating humor"]
}
```

### Optional Fields

```json
{
  "likely_opinions": {
    "premium_chocolate": "Sees value but questions if he can taste the difference",
    "gift_buying": "Relies on girlfriend's recommendations"
  }
}
```

---

## Field-by-Field Guide

### 1. Identity (name, age, occupation, location)

**Name:** Full realistic name. Mix of ethnicities.
- Good: "Marcus Chen", "Jennifer Martinez", "Aisha Williams"
- Bad: "Tech Guy 1", "Consumer A"

**Age:** Specific number, not range.
- Good: 28, 42, 58
- Bad: "25-34", "middle-aged"

**Occupation:** Specific job title with context.
- Good: "Software engineer at a fintech startup"
- Good: "Middle school English teacher"
- Bad: "Works in tech", "Teacher"

**Location:** City and state/country.
- Good: "Austin, TX", "Columbus, OH"
- Bad: "Urban", "Midwest"

### 2. Backstory (2-4 sentences)

The backstory provides **narrative context** that explains why this person thinks the way they do.

**Include:**
- Life circumstances (family, career stage, recent changes)
- Formative experiences (upbringing, pivotal moments)
- Current situation (what's on their mind)

**Examples:**

```
Marcus: "Moved from Seattle 2 years ago for a job opportunity. Works long
hours but values work-life balance on weekends. Grew up in a household
where food was fuel, not experience."
```
→ Explains why he's indifferent to premium food

```
Jennifer: "Single mom of two teenagers. Teaching for 18 years. Chocolate
is her 'me time' after the kids go to bed. Grew up in a big Mexican-American
family where food was central to gatherings."
```
→ Explains why chocolate is emotional/important to her

```
David: "Retired early after 30 years in medical device sales. Wife passed
3 years ago. Trying to stay active and social. Kids are grown and live
out of state."
```
→ Explains his pragmatic, no-nonsense approach

### 3. Category Relationship

How does this person relate to the **category you're researching**?

**Write in first person.** This becomes part of the persona's self-understanding.

**Spectrum of relationships:**
- Non-user: "I don't really think about chocolate. It's just there."
- Light user: "I buy it occasionally for guests."
- Regular user: "It's part of my weekly grocery run."
- Heavy user: "I have a secret stash the kids don't know about."
- Expert: "I've been to cacao farms in Ecuador."

**Examples:**

```
Marcus (indifferent): "Chocolate is an impulse buy at checkout for me.
Never seek it out specifically. My girlfriend introduced me to nicer
brands last year."
```

```
Jennifer (devotee): "Chocolate is almost sacred to me - it's my reward
at the end of a hard day. I have a secret stash the kids don't know about.
I've gotten pickier over the years."
```

```
David (pragmatic): "I buy chocolate for the grandkids when they visit.
For myself? Maybe a Snickers at the gas station."
```

### 4. Personality Traits (3-5 traits)

These affect **how** the persona responds, not just **what** they say.

**Good traits are specific and behavioral:**
- "analytical" → Will ask for evidence, compare options
- "skeptical of marketing" → Will push back on claims
- "nurturing" → Will consider others' needs
- "direct communicator" → Short sentences, no hedging

**Avoid vague traits:**
- "nice" → Too generic
- "normal" → Meaningless
- "average" → No differentiation

**Trait combinations create unique personalities:**

| Persona | Traits | Result |
|---------|--------|--------|
| Marcus | analytical, skeptical, direct | Questions claims, asks for proof |
| Jennifer | nurturing, articulate, brand-loyal | Explains reasoning, sticks with favorites |
| David | pragmatic, no-nonsense, generous | Brief answers, focused on value |
| Priya | health-conscious, research-driven, perfectionist | Cites data, justifies choices |

### 5. Speech Patterns (2-4 patterns)

How does this person **talk**? These create distinct voices.

**Examples:**

```
Marcus: ["Uses tech metaphors", "Tends to qualify statements",
         "Self-deprecating humor"]
→ "It's like debugging code - once you know what to look for..."
→ "I mean, I'm probably not the best person to ask, but..."
```

```
Jennifer: ["Vivid sensory descriptions", "References kids/students",
           "Complete sentences"]
→ "That perfect *snap* when you break off a piece..."
→ "Like when I finally sit down after the kids are in bed..."
```

```
David: ["Short sentences", "References to past", "Says 'look' to start"]
→ "Look, chocolate is chocolate."
→ "Back when my wife was alive..."
```

```
Bobby: ["Casual working-class directness", "Food/family references",
        "Says 'I'm telling you' for emphasis"]
→ "I'm telling you, my aunt would kill me if I brought Hershey's."
→ "We do chocolate at Christmas - big Italian family thing."
```

---

## Creating Diverse Panels

### Dimension Checklist

When creating a panel, vary across these dimensions:

| Dimension | Options |
|-----------|---------|
| **Category relationship** | Non-user, light, regular, heavy, expert |
| **Sentiment** | Enthusiastic, positive, neutral, skeptical, negative |
| **Demographics** | Age, gender, income, location, education |
| **Psychographics** | Values, lifestyle, priorities |
| **Personality** | Introverted/extroverted, analytical/intuitive |

### Example: 6-Person Premium Chocolate Panel

| # | Name | Relationship | Sentiment | Key Differentiator |
|---|------|--------------|-----------|-------------------|
| 1 | Marcus | Light user (girlfriend-influenced) | Skeptical | Can't taste difference |
| 2 | Jennifer | Heavy user (ritual) | Positive | Emotional connection |
| 3 | David | Non-user (pragmatic) | Neutral | Value-focused |
| 4 | Priya | Regular (health-focused) | Positive | Research-driven |
| 5 | Bobby | Occasion-based (traditions) | Positive | Family/culture |
| 6 | Aisha | Regular (story-driven) | Enthusiastic | Ethics/sourcing |

**Note:** No two personas share the same combination of relationship + sentiment.

---

## Common Mistakes

### 1. Demographics Without Narrative

❌ Bad:
```json
{
  "name": "Consumer 1",
  "age": 35,
  "income": "high",
  "backstory": "Works in tech."
}
```

✅ Good:
```json
{
  "name": "Marcus Chen",
  "age": 28,
  "backstory": "Moved from Seattle 2 years ago. Works long hours but values
               work-life balance on weekends. Grew up where food was fuel."
}
```

### 2. Everyone Is an Expert

❌ Bad: All 6 personas "appreciate quality" and "can taste the difference"

✅ Good: Include skeptics, non-users, and people who don't care

### 3. Same Speech Patterns

❌ Bad: Everyone speaks in complete, articulate sentences

✅ Good:
- Marcus: Qualifies everything, uses "like" and "you know"
- David: Short sentences, no fluff
- Bobby: Casual, references family constantly

### 4. Contradictory Traits

❌ Bad: "Health-conscious" + "eats chocolate daily"

✅ Good: "Health-conscious" + "researches before buying" + "justifies indulgence"

### 5. Stereotyping

❌ Bad: Italian person only talks about family and food

✅ Good: Bobby is Italian-American but also a business owner, skeptical of trends, and practical about money

---

## Generating Personas with Claude

You can ask Claude to generate personas from a recruitment spec:

**Prompt:**
```
Create 6 personas for a focus group on premium chocolate.

Recruitment criteria:
- Mix of ages 25-60
- Mix of genders
- Income $50K+ (need to afford premium)
- Include: 2 heavy users, 2 regular users, 2 light/non-users
- Geographic diversity (not all coastal cities)

For each persona, provide:
- id, name, age, occupation, location
- backstory (2-3 sentences explaining who they are)
- category_relationship (how they relate to premium chocolate)
- personality_traits (3-5 behavioral traits)
- speech_patterns (2-4 patterns for how they talk)

Make each persona genuinely different. Avoid stereotypes.
Output as JSON array.
```

**Review the output for:**
- Distinct category relationships
- Varied sentiment toward the category
- Unique speech patterns
- No duplicate personality combinations

---

## Full Example

```json
{
  "id": 1,
  "name": "Marcus Chen",
  "age": 28,
  "occupation": "Software engineer at a fintech startup",
  "location": "Austin, TX",
  "backstory": "Moved from Seattle 2 years ago for a job opportunity. Works long hours but values work-life balance on weekends. Grew up in a household where food was fuel, not experience. His girlfriend has been trying to expand his palate.",
  "category_relationship": "Chocolate is an impulse buy at checkout for me. Never seek it out specifically. My girlfriend introduced me to nicer brands last year - she gets frustrated when I say I can't taste the difference between Lindt and Godiva.",
  "personality_traits": [
    "analytical",
    "skeptical of marketing claims",
    "price-sensitive despite good income",
    "direct communicator",
    "curious but needs convincing"
  ],
  "speech_patterns": [
    "Uses tech metaphors and analogies",
    "Tends to qualify statements with 'I mean' or 'like'",
    "Asks follow-up questions",
    "Self-deprecating humor about his own tastes"
  ],
  "likely_opinions": {
    "premium_chocolate": "Sees the appeal but questions if he can actually taste the difference",
    "gift_buying": "Relies on girlfriend's recommendations, feels out of his depth"
  }
}
```

---

## Adding to audiences.json

```json
{
  "audiences": {
    "your_new_audience": {
      "category": "Your Category Name",
      "description": "Brief description of this audience",
      "personas": [
        { /* persona 1 */ },
        { /* persona 2 */ },
        { /* persona 3 */ }
      ]
    }
  }
}
```

After adding, test with:
```bash
curl http://localhost:8000/audiences/your_new_audience
```
