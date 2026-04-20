from dotenv import load_dotenv
load_dotenv()
from unittest import result
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import google.generativeai as genai
import os
import json
import re


genai.api_key = os.environ.get("GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

print("GOOGLE_API_KEY LOADED:", bool(os.getenv("GEMINI_API_KEY")))
print("MODEL READY:", model is not None)
def _get_allowed_origins() -> list:
    """Return the configured CORS origin allowlist."""
    configured_origins = os.environ.get("CORS_ALLOWED_ORIGINS")
    if configured_origins:
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
import random


class _RandomGeneratorCompat:
    def __init__(self, seed=None):
        self._rng = random.Random(seed)

    def random(self):
        return self._rng.random()

    def uniform(self, a, b):
        return self._rng.uniform(a, b)

    def randint(self, a, b):
        return self._rng.randint(a, b)

    def integers(self, low, high=None):
        if high is None:
            return self._rng.randrange(low)
        return self._rng.randrange(low, high)

    def choice(self, seq):
        return self._rng.choice(seq)

    def shuffle(self, seq):
        self._rng.shuffle(seq)


class _NumpyRandomCompat:
    @staticmethod
    def default_rng(seed=None):
        return _RandomGeneratorCompat(seed)


class _NumpyCompat:
    random = _NumpyRandomCompat()


np = _NumpyCompat()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": _get_allowed_origins()}})

# ---------------------------------------------------------------------------
# Mock scenario content helpers
# ---------------------------------------------------------------------------

SCENARIO_TEMPLATES = {
    "default": {
        "most_likely": {
            "outcome": "The situation unfolds as expected with moderate resistance.",
            "reasoning": "Based on current patterns, the most probable path follows existing momentum and constraints.",
            "rippleEffect": "Initial friction gives way to gradual adaptation, reshaping habits over the following weeks.",
        },
        "likely": {
            "outcome": "A partial shift occurs, with mixed results and unexpected learnings.",
            "reasoning": "External factors introduce variability, redirecting some energy toward unplanned opportunities.",
            "rippleEffect": "New connections and perspectives emerge, opening doors that weren't previously visible.",
        },
        "less_likely": {
            "outcome": "A surprising breakthrough fundamentally changes the trajectory.",
            "reasoning": "Low-probability catalysts sometimes compound, creating disproportionate positive outcomes.",
            "rippleEffect": "A cascade of secondary changes accelerates growth across multiple life areas simultaneously.",
        },
        "betterDecision": "Consider breaking the scenario into smaller, reversible steps. Gather feedback early and adjust before committing fully.",
        "projection": {
            "mentalState": "Initial uncertainty transitions to clarity as small wins accumulate over the first two weeks.",
            "performance": "Output dips slightly in week one as focus shifts, then rebounds 15–20% above baseline by day 21.",
            "riskLevel": "Moderate – manageable with consistent review checkpoints every 7 days.",
        },
    }
}


def _build_response(scenario: str) -> dict:
    """Generate outcome probabilities and mock content for the given scenario."""
    rng = np.random.default_rng()

    # Generate probabilities that sum to 1.0
    most_likely = round(float(rng.uniform(0.65, 0.85)), 2)
    remaining = round(1.0 - most_likely, 2)
    likely_raw = round(remaining * 0.70)
    likely = round(likely_raw, 2)
    less_likely = round(remaining - likely, 2)

    # Correct any floating-point drift so the three values sum exactly to 1.0
    total = round(most_likely + likely + less_likely, 2)
    if total != 1.0:
        less_likely = round(less_likely + (1.0 - total), 2)

    tpl = SCENARIO_TEMPLATES["default"]

    outcomes = [
        {
            "label": "Most Likely",
            "probability": most_likely,
            "outcome": tpl["most_likely"]["outcome"],
            "reasoning": tpl["most_likely"]["reasoning"],
            "rippleEffect": tpl["most_likely"]["rippleEffect"],
        },
        {
            "label": "Likely",
            "probability": likely,
            "outcome": tpl["likely"]["outcome"],
            "reasoning": tpl["likely"]["reasoning"],
            "rippleEffect": tpl["likely"]["rippleEffect"],
        },
        {
            "label": "Less Likely",
            "probability": less_likely,
            "outcome": tpl["less_likely"]["outcome"],
            "reasoning": tpl["less_likely"]["reasoning"],
            "rippleEffect": tpl["less_likely"]["rippleEffect"],
        },
    ]

    return {
        "outcomes": outcomes,
        "betterDecision": tpl["betterDecision"],
        "projection": tpl["projection"],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------



@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        data = request.get_json(silent=True)

        if not data or not data.get("scenario"):
            return jsonify({"error": "scenario required"}), 400

        scenario = data["scenario"]

        result = call_gemini(scenario)

        return jsonify(result)

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({
            "error": "server crashed",
            "details": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

def call_gemini(scenario: str):
    prompt = f"""
You are a decision intelligence engine.

Analyze this scenario deeply and personally:

"{scenario}"

You MUST:
- Treat each scenario as a unique case study. Do not reuse mental templates across different inputs.
- tailor ALL reasoning to the exact scenario
- avoid generic advice
- avoid templates
- behave like a strategist simulating real consequences
You MUST:
- tailor ALL reasoning to the exact scenario
- avoid generic advice
- avoid templates
- behave like a strategist simulating real consequences

STRICT OUTPUT LIMITS:
- Each field MUST be max 1 to 2 short sentences
- Each field MUST be under 25 words
- Reasoning MUST be brief and direct (no paragraphs)
- RippleEffect MUST be 1 to 2 sentences max
- BetterDecision MUST be 1 to 2 sentences max
- No repetition across fields

STYLE:
- Be concise and factual
- No filler words
- No academic explanations
Use extremely concise, natural language.
Return ONLY valid JSON:

{{
  "outcomes": [
    {{
      "label": "Most Likely",
      "probability": 0.7,
      "outcome": "",
      "reasoning": "",
      "rippleEffect": ""
    }},
    {{
      "label": "Likely",
      "probability": 0.2,
      "outcome": "",
      "reasoning": "",
      "rippleEffect": ""
    }},
    {{
      "label": "Less Likely",
      "probability": 0.1,
      "outcome": "",
      "reasoning": "",
      "rippleEffect": ""
    }}
  ],
  "betterDecision": "",
  "projection": {{
    "mentalState": "",
    "performance": "",
    "riskLevel": "Low|Moderate|High"
  }}
}}

Rules:
- NO generic business advice
- MUST reference scenario specifics
- NO explanations outside JSON
"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    # remove markdown wrappers
    text = text.replace("```json", "").replace("```", "").strip()

    import json, re

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())

        # HARD fallback (prevents crash)
        return {
            "error": "Invalid Gemini response",
            "raw": text
        }
    
if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, port=5000)
