# Consequence Engine

AI-powered "Consequence Engine" that simulates outcomes for real-life decisions. Input a scenario, get ranked possibilities with probability labels, behavioral reasoning, and ripple effects. Includes a smarter alternative and 30-day projection to help users act with clarity, foresight, and reduced regret.

## Project Structure

```
Consequence-Engine/
├── backend/          # Python Flask API
│   ├── app.py
│   └── requirements.txt
└── frontend/         # React (Vite) + Tailwind CSS
    ├── src/
    │   ├── components/
    │   │   ├── InputBox.jsx
    │   │   ├── OutcomeCard.jsx
    │   │   ├── ResultsGrid.jsx
    │   │   ├── SmarterDecision.jsx
    │   │   └── ProjectionSection.jsx
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+

---

## Running the Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The Flask API will be available at `http://localhost:5000`.

### API Endpoint

**POST** `/simulate`

**Request body:**
```json
{ "scenario": "I am thinking about quitting my job to start a business." }
```

**Response:**
```json
{
  "outcomes": [
    {
      "label": "Most Likely",
      "probability": 0.72,
      "outcome": "...",
      "reasoning": "...",
      "rippleEffect": "..."
    },
    { "label": "Likely", "probability": 0.20, "outcome": "...", "reasoning": "...", "rippleEffect": "..." },
    { "label": "Less Likely", "probability": 0.08, "outcome": "...", "reasoning": "...", "rippleEffect": "..." }
  ],
  "betterDecision": "...",
  "projection": {
    "mentalState": "...",
    "performance": "...",
    "riskLevel": "..."
  }
}
```

---

## Running the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

> The Vite dev server automatically proxies `/simulate` requests to `http://localhost:5000`, so both servers must be running simultaneously.

---

## Building for Production

```bash
cd frontend
npm run build
```

The static output will be in `frontend/dist/`.
