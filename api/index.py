"""
Focus Group API - Vercel Serverless Function
"""

import os
import sys
import json
from typing import List, Optional, Dict, Any
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import FocusGroupEngine

# Config path
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audiences.json")


def get_config() -> dict:
    """Load audiences config"""
    if not os.path.exists(CONFIG_PATH):
        return {"audiences": {}}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


class handler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message: str, status: int = 400):
        self._send_json({"error": message}, status)

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        # Health check
        if path == '' or path == '/':
            return self._send_json({
                "status": "ok",
                "service": "focus-group-api",
                "version": "2.0.0",
                "mode": "stateless"
            })

        # List audiences
        if path == '/audiences':
            config = get_config()
            audiences = []
            for aid, data in config.get("audiences", {}).items():
                audiences.append({
                    "id": aid,
                    "category": data.get("category", ""),
                    "description": data.get("description", ""),
                    "persona_count": len(data.get("personas", []))
                })
            return self._send_json({"audiences": audiences})

        # Get specific audience
        if path.startswith('/audiences/'):
            parts = path.split('/')
            if len(parts) == 3:
                audience_id = parts[2]
                config = get_config()
                if audience_id not in config.get("audiences", {}):
                    return self._send_error(f"Audience '{audience_id}' not found", 404)

                data = config["audiences"][audience_id]
                personas = []
                for p in data.get("personas", []):
                    personas.append({
                        "id": p["id"],
                        "name": p["name"],
                        "age": p["age"],
                        "occupation": p["occupation"],
                        "location": p["location"],
                        "backstory": p["backstory"],
                        "personality_traits": p.get("personality_traits", []),
                        "image": p.get("image", "")
                    })
                return self._send_json({
                    "id": audience_id,
                    "category": data.get("category", ""),
                    "personas": personas
                })

        return self._send_error("Not found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

        try:
            request_data = json.loads(body)
        except json.JSONDecodeError:
            return self._send_error("Invalid JSON", 400)

        # Ask group: POST /audiences/{audience_id}/ask
        if path.startswith('/audiences/') and path.endswith('/ask'):
            parts = path.split('/')
            if len(parts) == 4:
                audience_id = parts[2]
                config = get_config()
                if audience_id not in config.get("audiences", {}):
                    return self._send_error(f"Audience '{audience_id}' not found", 404)

                question = request_data.get("question")
                if not question:
                    return self._send_error("Missing 'question' field", 400)

                history = request_data.get("history", [])

                try:
                    engine = FocusGroupEngine()
                    result = engine.ask_stateless(
                        question=question,
                        audience_id=audience_id,
                        history=history,
                        config_path=CONFIG_PATH
                    )

                    return self._send_json({
                        "responses": result["responses"],
                        "history": result["history"]
                    })
                except Exception as e:
                    import traceback
                    return self._send_error(f"Engine error: {str(e)} | {traceback.format_exc()}", 500)

        # Ask specific persona: POST /audiences/{audience_id}/ask/{persona_id}
        if '/ask/' in path:
            parts = path.split('/')
            if len(parts) == 5 and parts[3] == 'ask':
                audience_id = parts[2]
                try:
                    persona_id = int(parts[4])
                except ValueError:
                    return self._send_error("Invalid persona_id", 400)

                config = get_config()
                if audience_id not in config.get("audiences", {}):
                    return self._send_error(f"Audience '{audience_id}' not found", 404)

                question = request_data.get("question")
                if not question:
                    return self._send_error("Missing 'question' field", 400)

                history = request_data.get("history", [])

                engine = FocusGroupEngine()
                try:
                    result = engine.ask_persona_stateless(
                        persona_id=persona_id,
                        question=question,
                        audience_id=audience_id,
                        history=history,
                        config_path=CONFIG_PATH
                    )
                except ValueError as e:
                    return self._send_error(str(e), 404)

                return self._send_json({
                    "response": result["response"],
                    "history": result["history"]
                })

        return self._send_error("Not found", 404)
