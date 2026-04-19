from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import os
import json
import re
import requests

# Initialize OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")


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


def _build_template_response(scenario: str) -> dict:
    """Fallback template response when AI is unavailable."""
    rng = np.random.default_rng()

    # Generate probabilities that sum to 1.0
    most_likely = round(float(rng.uniform(0.65, 0.85)), 2)
    remaining = round(1.0 - most_likely, 2)
    likely_raw = remaining * 0.70
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


def _build_response(scenario: str) -> dict:
    """Generate AI-powered outcome analysis for the given scenario."""
    if not api_key:
        print("Warning: OpenAI API key not configured. Using template responses.")
        return _build_template_response(scenario)
    
    try:
        # Use OpenAI API to generate contextual outcomes
        prompt = f"""Analyze this decision scenario and provide three possible outcomes with probabilities.

Scenario: "{scenario}"

Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):
{{
  "outcomes": [
    {{
      "label": "Most Likely",
      "probability": 0.XX,
      "outcome": "A concise description of what would most likely happen",
      "reasoning": "Why this is the most probable outcome based on the scenario",
      "rippleEffect": "Secondary effects and downstream consequences"
    }},
    {{
      "label": "Likely",
      "probability": 0.XX,
      "outcome": "An alternative positive or neutral outcome",
      "reasoning": "Why this could happen given external factors",
      "rippleEffect": "How this outcome would influence other areas"
    }},
    {{
      "label": "Less Likely",
      "probability": 0.XX,
      "outcome": "An unlikely but possible breakthrough outcome",
      "reasoning": "Low-probability catalysts that could lead to this",
      "rippleEffect": "Unexpected positive cascading effects"
    }}
  ],
  "betterDecision": "A specific, actionable recommendation to improve the decision",
  "projection": {{
    "mentalState": "How the person's mental state might evolve over 30 days",
    "performance": "Expected performance impact in the first month",
    "riskLevel": "Risk assessment with specific mitigations"
  }}
}}

Ensure probabilities sum to 1.0 and are realistic for the scenario."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert decision analyst. Provide insightful, personalized outcome analysis based on the user's scenario.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1200,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return _build_template_response(scenario)

        data = response.json()
        
        if "choices" not in data or len(data["choices"]) == 0:
            print(f"Unexpected OpenAI response: {data}")
            return _build_template_response(scenario)

        content = data["choices"][0]["message"]["content"].strip()

        # Try to extract JSON from the response
        try:
            # First try direct JSON parsing
            result = json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON in the content (in case there's extra text)
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                print(f"Could not parse JSON from response: {content}")
                return _build_template_response(scenario)

        # Validate and normalize probabilities
        outcomes = result.get("outcomes", [])
        prob_sum = sum(o.get("probability", 0) for o in outcomes)
        if prob_sum > 0:
            for outcome in outcomes:
                outcome["probability"] = round(outcome["probability"] / prob_sum, 2)

        return result

    except Exception as e:
        # Fallback to template if AI fails
        print(f"Error calling OpenAI API: {e}")
        return _build_template_response(scenario)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("scenario"), str) or not data["scenario"].strip():
        return jsonify({"error": "A non-empty 'scenario' string is required."}), 400

    scenario = data["scenario"].strip()
    result = _build_response(scenario)
    return jsonify(result), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, port=5001)
