from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)

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
    app.run(debug=debug, port=5000)
