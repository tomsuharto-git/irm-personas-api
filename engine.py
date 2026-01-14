"""
Focus Group Engine - Core chat engine with persona memory and consistency enforcement
"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from anthropic import Anthropic


@dataclass
class Persona:
    """Rich persona with narrative anchors for consistent responses"""
    id: int
    name: str
    age: int
    occupation: str
    location: str

    # Narrative anchors - these enforce consistency
    backstory: str
    category_relationship: str

    # Personality
    personality_traits: List[str]
    speech_patterns: List[str]

    # Optional enrichment
    likely_opinions: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "location": self.location,
            "backstory": self.backstory,
            "category_relationship": self.category_relationship,
            "personality_traits": self.personality_traits,
            "speech_patterns": self.speech_patterns,
            "likely_opinions": self.likely_opinions
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Persona":
        return cls(
            id=data["id"],
            name=data["name"],
            age=data["age"],
            occupation=data["occupation"],
            location=data["location"],
            backstory=data["backstory"],
            category_relationship=data["category_relationship"],
            personality_traits=data.get("personality_traits", []),
            speech_patterns=data.get("speech_patterns", []),
            likely_opinions=data.get("likely_opinions", {})
        )


@dataclass
class Response:
    """A response from a persona"""
    persona_id: int
    persona_name: str
    text: str

    def to_dict(self) -> dict:
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "text": self.text
        }


class FocusGroupEngine:
    """
    Core engine for focus group chat.

    Manages:
    - Audience/persona loading from config
    - Conversation history per persona (for consistency)
    - Response generation with full persona context
    - AI-driven responder selection
    """

    def __init__(self, api_key: str = None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.personas: List[Persona] = []
        self.audience_id: str = None
        self.category: str = None

        # Conversation state
        self.transcript: List[Dict] = []  # Full conversation
        self.persona_history: Dict[int, List[str]] = {}  # What each persona has said

    def load_audience(self, audience_id: str, config_path: str = None) -> List[Persona]:
        """Load an audience from the config file"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "audiences.json")

        with open(config_path, "r") as f:
            config = json.load(f)

        if audience_id not in config["audiences"]:
            available = list(config["audiences"].keys())
            raise ValueError(f"Audience '{audience_id}' not found. Available: {available}")

        audience_data = config["audiences"][audience_id]
        self.audience_id = audience_id
        self.category = audience_data.get("category", "")

        self.personas = [Persona.from_dict(p) for p in audience_data["personas"]]

        # Initialize persona history
        self.persona_history = {p.id: [] for p in self.personas}
        self.transcript = []

        return self.personas

    def set_personas(self, personas: List[Persona], category: str = ""):
        """Set personas directly (for dynamic generation)"""
        self.personas = personas
        self.category = category
        self.persona_history = {p.id: [] for p in self.personas}
        self.transcript = []

    def _build_persona_prompt(self, persona: Persona) -> str:
        """Build the system prompt for a persona - enforces consistency"""

        # Get this persona's previous statements
        previous = self.persona_history.get(persona.id, [])
        history_text = ""
        if previous:
            history_text = "\n\nWHAT YOU'VE ALREADY SAID IN THIS CONVERSATION:\n"
            for stmt in previous[-5:]:  # Last 5 statements
                history_text += f"- \"{stmt}\"\n"
            history_text += "\nDo NOT contradict these. You can reference them naturally."

        return f"""You ARE {persona.name}. You are participating in a focus group discussion.

WHO YOU ARE:
- Name: {persona.name}
- Age: {persona.age}
- Occupation: {persona.occupation}
- Location: {persona.location}

YOUR STORY:
{persona.backstory}

YOUR RELATIONSHIP TO {self.category.upper() if self.category else 'THIS TOPIC'}:
{persona.category_relationship}

YOUR PERSONALITY:
{', '.join(persona.personality_traits)}

HOW YOU SPEAK:
{', '.join(persona.speech_patterns)}
{history_text}

---

CRITICAL INSTRUCTIONS:
1. Respond AS {persona.name} - stay in character completely
2. Use language natural to your background and personality
3. Reference your actual experiences and history
4. Don't sanitize your opinion - give your REAL view
5. Typical response: 2-4 sentences (but vary naturally - some answers are shorter)

NEVER DO THESE:
- Sound like a generic survey respondent
- Start with "I think..." every time (vary: "Honestly," "For me," "Look," "So," etc.)
- Use phrases like "quality matters to me" or "it depends"
- Contradict what you've already said
- Suddenly know things {persona.name} wouldn't know
- Use perfect grammar if that doesn't fit your character
- Use survey-speak like "I would say that..." or "In my opinion..."

Respond naturally and authentically as {persona.name}."""

    def _select_responders(self, question: str) -> List[int]:
        """Use AI to select which 2-4 personas would naturally respond"""

        # Build context about who's spoken recently
        recent_speakers = []
        for msg in self.transcript[-6:]:
            if msg["role"] == "persona":
                recent_speakers.append(msg["persona_name"])

        persona_summaries = []
        for p in self.personas:
            statements = len(self.persona_history.get(p.id, []))
            persona_summaries.append(
                f"- {p.name} ({p.age}, {p.occupation}): {p.personality_traits[0] if p.personality_traits else 'neutral'}. "
                f"Statements so far: {statements}"
            )

        prompt = f"""You are moderating a focus group. The moderator just asked:

"{question}"

Here are the participants:
{chr(10).join(persona_summaries)}

Recent speakers (last few responses): {', '.join(recent_speakers) if recent_speakers else 'None yet'}

Select 2-4 participants who would NATURALLY respond to this question. Consider:
1. Who has relevant experience/opinions based on their profile?
2. Who hasn't spoken recently and might want to contribute?
3. Natural group dynamics - some people talk more than others
4. The question topic - who would this resonate with?

Return ONLY a JSON array of participant names who should respond, in the order they'd speak.
Example: ["Marcus", "Jennifer", "David"]

Do NOT include everyone. Real focus groups have natural turn-taking."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse the response
        text = response.content[0].text.strip()

        # Extract JSON array
        import re
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            try:
                names = json.loads(match.group())
                # Convert names to persona IDs - handle partial name matches
                name_to_id = {}
                for p in self.personas:
                    name_to_id[p.name] = p.id
                    # Also add first name only
                    first_name = p.name.split()[0]
                    name_to_id[first_name] = p.id

                selected = [name_to_id[n] for n in names if n in name_to_id]
                if selected:
                    return selected
            except json.JSONDecodeError:
                pass

        # Fallback: return first 3 personas
        return [p.id for p in self.personas[:3]]

    def _generate_response(self, persona: Persona, question: str) -> str:
        """Generate a response from a specific persona"""

        system_prompt = self._build_persona_prompt(persona)

        # Include recent conversation context
        recent_context = ""
        for msg in self.transcript[-8:]:
            if msg["role"] == "moderator":
                recent_context += f"\nModerator: {msg['text']}"
            elif msg["role"] == "persona":
                recent_context += f"\n{msg['persona_name']}: {msg['text']}"

        user_message = question
        if recent_context:
            user_message = f"[Recent conversation]{recent_context}\n\n---\n\nModerator's current question: {question}"

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            temperature=0.9,  # High for personality variance
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        return response.content[0].text.strip()

    def ask(self, question: str) -> List[Response]:
        """
        Ask the group a question. AI selects natural responders.

        Returns responses from 2-4 personas.
        """
        if not self.personas:
            raise ValueError("No personas loaded. Call load_audience() first.")

        # Record moderator question
        self.transcript.append({
            "role": "moderator",
            "text": question
        })

        # Select who responds
        responder_ids = self._select_responders(question)

        responses = []
        for pid in responder_ids:
            persona = next((p for p in self.personas if p.id == pid), None)
            if not persona:
                continue

            text = self._generate_response(persona, question)

            # Record in persona history
            self.persona_history[pid].append(text)

            # Record in transcript
            self.transcript.append({
                "role": "persona",
                "persona_id": pid,
                "persona_name": persona.name,
                "text": text
            })

            responses.append(Response(
                persona_id=pid,
                persona_name=persona.name,
                text=text
            ))

        return responses

    def ask_persona(self, persona_id: int, question: str) -> Response:
        """Ask a specific persona directly (1:1 mode)"""

        persona = next((p for p in self.personas if p.id == persona_id), None)
        if not persona:
            raise ValueError(f"Persona {persona_id} not found")

        # Record moderator question (directed)
        self.transcript.append({
            "role": "moderator",
            "text": f"[To {persona.name}] {question}"
        })

        text = self._generate_response(persona, question)

        # Record
        self.persona_history[persona_id].append(text)
        self.transcript.append({
            "role": "persona",
            "persona_id": persona_id,
            "persona_name": persona.name,
            "text": text
        })

        return Response(
            persona_id=persona_id,
            persona_name=persona.name,
            text=text
        )

    def get_transcript(self) -> List[Dict]:
        """Get the full conversation transcript"""
        return self.transcript

    def get_transcript_text(self) -> str:
        """Get transcript as formatted text"""
        lines = []
        for msg in self.transcript:
            if msg["role"] == "moderator":
                lines.append(f"\nMODERATOR: {msg['text']}")
            else:
                lines.append(f"\n{msg['persona_name'].upper()}: {msg['text']}")
        return "\n".join(lines)

    def reset_conversation(self):
        """Clear conversation history but keep personas"""
        self.transcript = []
        self.persona_history = {p.id: [] for p in self.personas}

    # ========== STATELESS MODE ==========
    # These methods accept/return full state for serverless deployments

    def _rebuild_state_from_history(self, history: List[Dict]):
        """Rebuild internal state from conversation history"""
        self.transcript = history.copy()
        self.persona_history = {p.id: [] for p in self.personas}

        # Extract what each persona has said
        for msg in history:
            if msg.get("role") == "persona":
                pid = msg.get("persona_id")
                if pid in self.persona_history:
                    self.persona_history[pid].append(msg.get("text", ""))

    def ask_stateless(
        self,
        question: str,
        audience_id: str,
        history: List[Dict] = None,
        config_path: str = None
    ) -> Dict:
        """
        Stateless ask - accepts history, returns updated history.

        Args:
            question: The moderator's question
            audience_id: Which audience to use
            history: Previous conversation (list of message dicts)
            config_path: Optional path to audiences.json

        Returns:
            {
                "responses": [...],
                "history": [... updated with new messages ...]
            }
        """
        # Load audience
        self.load_audience(audience_id, config_path)

        # Rebuild state from history
        if history:
            self._rebuild_state_from_history(history)

        # Ask the question (updates internal state)
        responses = self.ask(question)

        return {
            "responses": [r.to_dict() for r in responses],
            "history": self.transcript.copy()
        }

    def ask_persona_stateless(
        self,
        persona_id: int,
        question: str,
        audience_id: str,
        history: List[Dict] = None,
        config_path: str = None
    ) -> Dict:
        """
        Stateless ask_persona - accepts history, returns updated history.

        Args:
            persona_id: Which persona to ask
            question: The moderator's question
            audience_id: Which audience to use
            history: Previous conversation
            config_path: Optional path to audiences.json

        Returns:
            {
                "response": {...},
                "history": [... updated ...]
            }
        """
        # Load audience
        self.load_audience(audience_id, config_path)

        # Rebuild state from history
        if history:
            self._rebuild_state_from_history(history)

        # Ask the persona
        response = self.ask_persona(persona_id, question)

        return {
            "response": response.to_dict(),
            "history": self.transcript.copy()
        }
