"""
Focus Group API - Stateless FastAPI backend

All conversation state is managed by the client. Each request includes
the conversation history and returns the updated history.

Endpoints:
    GET  /                                   - Health check
    GET  /audiences                          - List available audiences
    GET  /audiences/{audience_id}            - Get audience details + personas
    POST /audiences/{audience_id}/ask        - Ask the group (stateless)
    POST /audiences/{audience_id}/ask/{pid}  - Ask specific persona (stateless)
"""

import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .engine import FocusGroupEngine

app = FastAPI(
    title="Focus Group Chat API",
    description="Stateless synthetic focus group chat - client manages conversation history",
    version="2.0.0"
)

# CORS - configure for your domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config path
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "audiences.json")


# ========== Request/Response Models ==========

class Message(BaseModel):
    role: str  # "moderator" or "persona"
    text: str
    persona_id: Optional[int] = None
    persona_name: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    history: Optional[List[Message]] = None


class PersonaResponse(BaseModel):
    persona_id: int
    persona_name: str
    text: str


class AskResponse(BaseModel):
    responses: List[PersonaResponse]
    history: List[Message]


class AskPersonaResponse(BaseModel):
    response: PersonaResponse
    history: List[Message]


class PersonaSummary(BaseModel):
    id: int
    name: str
    age: int
    occupation: str
    location: str
    backstory: str
    personality_traits: List[str]


class AudienceResponse(BaseModel):
    id: str
    category: str
    personas: List[PersonaSummary]


# ========== Helper Functions ==========

def get_config() -> dict:
    """Load audiences config"""
    if not os.path.exists(CONFIG_PATH):
        return {"audiences": {}}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def messages_to_dicts(messages: List[Message]) -> List[dict]:
    """Convert Pydantic models to dicts for engine"""
    if not messages:
        return []
    return [m.model_dump() for m in messages]


def dicts_to_messages(dicts: List[dict]) -> List[Message]:
    """Convert engine dicts to Pydantic models"""
    return [Message(**d) for d in dicts]


# ========== Endpoints ==========

@app.get("/")
def health_check():
    """Health check"""
    return {"status": "ok", "service": "focus-group-api", "version": "2.0.0", "mode": "stateless"}


@app.get("/audiences")
def list_audiences():
    """List all available audiences"""
    config = get_config()
    audiences = []
    for aid, data in config.get("audiences", {}).items():
        audiences.append({
            "id": aid,
            "category": data.get("category", ""),
            "description": data.get("description", ""),
            "persona_count": len(data.get("personas", []))
        })
    return {"audiences": audiences}


@app.get("/audiences/{audience_id}", response_model=AudienceResponse)
def get_audience(audience_id: str):
    """Get details about a specific audience including all personas"""
    config = get_config()
    if audience_id not in config.get("audiences", {}):
        raise HTTPException(status_code=404, detail=f"Audience '{audience_id}' not found")

    data = config["audiences"][audience_id]
    personas = []
    for p in data.get("personas", []):
        personas.append(PersonaSummary(
            id=p["id"],
            name=p["name"],
            age=p["age"],
            occupation=p["occupation"],
            location=p["location"],
            backstory=p["backstory"],
            personality_traits=p.get("personality_traits", [])
        ))

    return AudienceResponse(
        id=audience_id,
        category=data.get("category", ""),
        personas=personas
    )


@app.post("/audiences/{audience_id}/ask", response_model=AskResponse)
def ask_group(audience_id: str, request: AskRequest):
    """
    Ask the group a question (stateless).

    Send conversation history, get responses + updated history.
    AI selects 2-4 personas who would naturally respond.
    """
    config = get_config()
    if audience_id not in config.get("audiences", {}):
        raise HTTPException(status_code=404, detail=f"Audience '{audience_id}' not found")

    engine = FocusGroupEngine()
    result = engine.ask_stateless(
        question=request.question,
        audience_id=audience_id,
        history=messages_to_dicts(request.history) if request.history else None,
        config_path=CONFIG_PATH
    )

    return AskResponse(
        responses=[PersonaResponse(**r) for r in result["responses"]],
        history=dicts_to_messages(result["history"])
    )


@app.post("/audiences/{audience_id}/ask/{persona_id}", response_model=AskPersonaResponse)
def ask_persona(audience_id: str, persona_id: int, request: AskRequest):
    """
    Ask a specific persona directly (1:1 mode, stateless).

    Send conversation history, get response + updated history.
    """
    config = get_config()
    if audience_id not in config.get("audiences", {}):
        raise HTTPException(status_code=404, detail=f"Audience '{audience_id}' not found")

    engine = FocusGroupEngine()

    try:
        result = engine.ask_persona_stateless(
            persona_id=persona_id,
            question=request.question,
            audience_id=audience_id,
            history=messages_to_dicts(request.history) if request.history else None,
            config_path=CONFIG_PATH
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return AskPersonaResponse(
        response=PersonaResponse(**result["response"]),
        history=dicts_to_messages(result["history"])
    )


# Vercel serverless handler
from mangum import Mangum
handler = Mangum(app)

# Run locally: uvicorn focus_group.api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
