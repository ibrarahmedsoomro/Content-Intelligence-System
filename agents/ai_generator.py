import os
import json
from typing import Optional, Dict, Any

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class GeminiAgentBridge:
    """
    Expert Mode Gemini AI Generation Engine:
    Uses google-genai SDK (gemini-3.8-flash) for live, creative agent synthesis when GEMINI_API_KEY is available.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        if self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[GeminiBridge] Failed to init client: {e}")

    def is_active(self) -> bool:
        return self.client is not None

    def generate_creative_arc(self, topic: str, angle: str, question: str, audience_style: str) -> Optional[Dict[str, Any]]:
        if not self.is_active():
            return None
        
        prompt = f"""You are a master documentary director for YouTube.
Generate a high-tension 5-beat narrative arc for:
Topic: {topic}
Strategic Angle: {angle}
Core Viewer Question: {question}
Channel Style: {audience_style}

Return strictly valid JSON with this schema:
{{
  "core_thesis": "One powerful sentence explaining the hidden mechanism",
  "hook_promise": "Opening hook promise within first 15s",
  "beats": [
    {{
      "beat_number": 1,
      "title": "Myth & Instant Hook",
      "narrative_goal": "...",
      "tension_level": 7,
      "key_revelation": "...",
      "visual_anchor": "..."
    }}
  ]
}}"""
        try:
            interaction = self.client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )
            text = interaction.output_text or ""
            # Clean json fences if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"[GeminiBridge] Error generating arc: {e}")
            return None
