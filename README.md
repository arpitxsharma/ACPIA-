# ACPIA+

**Explainable Multi-Agent Child Protection Investigation Assistant**

Built for HAC'KP 2026.
---

## The problem

In child protection investigations, police have to manually work through thousands of
chats, images, videos, audio files, and documents per case. Finding the critical
evidence, connecting suspects across accounts, and figuring out which cases need
attention *first* is slow, and that delay has real consequences.

## Our solution

ACPIA+ is a multi-agent system where each agent has one clear job:

- **Evidence Agent** — extracts text from every evidence file (OCR on images, Whisper
  on audio, direct extraction from chats/PDFs/JSON), then pulls out entities (usernames,
  accounts, emails)
- **Correlation Agent** — finds which entities appear together across evidence and
  builds a relationship graph, so investigators can see who/what is connected
- **Timeline Agent** — orders every evidence item chronologically with a readable
  description
- **Risk Agent** — combines signals from the other agents into a transparent priority
  score, with every contributing factor shown and traceable to real evidence
- **AI Copilot** — answers investigator questions using retrieval-augmented generation
  (FAISS + Gemini) grounded only in the case's actual evidence, always citing evidence
  IDs

**The part we care about most: every single output is explainable.** Every
recommendation shows its confidence, the evidence it's based on, and an honest
uncertainty note. Nothing the AI produces is a black box, and nothing is final until a
human investigator approves it.

## Features
- Investigator dashboard with case stats and live agent activity
- Full case view: evidence, correlation graph, timeline, risk score, AI copilot — six
  tabs, each backed by a real agent
- "Why was this case prioritized?" — a dedicated explainability breakdown for the risk
  score
- Human-in-the-loop controls: Approve / Reject / Request More Evidence — the AI never
  makes the final call
- A "LOAD DEMO CASE" button that runs the entire pipeline live, evidence in and results
  out, with real-time agent status
- Demo-mode fallbacks for Whisper transcription and Gemini generation, so the pipeline
  still works end-to-end even without internet access during a live demo

## Architecture

```
                 DIGITAL EVIDENCE
                        |
                        v
                 EVIDENCE AGENT
        (OCR, Whisper, PDF/text extraction,
              entity extraction)
                        |
            +-----------+-----------+
            |           |           |
            v           v           v
       CORRELATION   TIMELINE     RISK
         AGENT        AGENT       AGENT
    (entity graph) (chronology) (priority score)
            |           |           |
            +-----------+-----------+
                        |
                        v
                   AI COPILOT
          (FAISS retrieval + Gemini,
           grounded in case evidence)
                        |
                        v
                HUMAN INVESTIGATOR
             (Approve / Reject / More
                    evidence)
```

Explainability (confidence, reasons, evidence references, uncertainty) is a property of
every agent's output, not a separate feature bolted on — all four agents return the
same shared shape, and the frontend renders it with one reusable component
(`ExplainabilityPanel`).

## Tech stack

Deliberately kept small so it's easy to understand end to end and easy to defend in a
Q&A.
**Frontend:** React + Vite, plain CSS, no router (single-page state switching)
**Backend:** Python + FastAPI
**AI:** Gemini API (generation + embeddings), LangGraph for agent orchestration
(a compiled `StateGraph` with one node per agent, matching the architecture diagram)
**RAG:** FAISS for vector search, with a local TF-IDF fallback if Gemini embeddings
are unavailable
**Evidence processing:** Tesseract OCR, faster-whisper for audio transcription, pypdf
for PDF text extraction
**Data:** JSON files (no database — this is a single-demo-case PoC)

## Project structure

```
acpia-plus/
├── frontend/
│   ├── src/
│   │   ├── components/     # StatCard, EvidenceList, CorrelationGraph, etc.
│   │   ├── pages/           # Landing, Dashboard, CaseView
│   │   ├── data/             # local fallback data
│   │   ├── services/api.js  # all backend calls, with fallback logic
│   │   └── App.jsx
│   └── package.json
├── backend/
│   ├── agents/               # evidence_agent, correlation_agent, timeline_agent,
│   │                         # risk_agent, copilot, graph (LangGraph pipeline)
│   ├── services/             # OCR/Whisper, embeddings, Gemini client, data loading
│   ├── data/demo_case/       # synthetic evidence + cached agent outputs
│   ├── main.py                # FastAPI routes
│   └── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation

### Backend

```bash
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env
# then edit .env and add your GEMINI_API_KEY
```

You'll also need Tesseract OCR installed on your system (not a pip package):

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt install tesseract-ocr
```

### Frontend

```bash
cd frontend
npm install
```

## Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Required | Notes |
|---|---|---|
| `GEMINI_API_KEY` | No, but recommended | Get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey). Without it, the Evidence Agent's audio transcription and the AI Copilot both fall back to local/offline logic automatically — the app still works, just with lower-fidelity answers. |

## Running it

**Terminal 1 — backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`).

## Demo instructions

1. Landing page → **ENTER INVESTIGATOR CONSOLE**
2. Dashboard → **LOAD DEMO CASE** — watch the agent activity panel process live
3. You'll land on case `ACPIA-1024`. Walk through the tabs in order: **Evidence →
   Correlation → Timeline → Risk → Copilot**
4. On the **Risk** tab, scroll down to see the human review controls — click one to
   see the human-in-the-loop flow complete
5. On the **Copilot** tab, ask "Why was this case prioritized?" or click one of the
   suggested questions

If you restart the demo, delete `backend/data/demo_case/review_status.json` so the
review controls start fresh (unapproved) again.

## Synthetic data disclaimer

**Every piece of evidence in this project is fictional**, generated specifically for
this demo. No real names, phone numbers, email addresses, private conversations, or
any real personal data appear anywhere in this repository. The synthetic evidence
files (chat logs, a generated screenshot image, a generated PDF, and a synthesized
voice note) were created purely to demonstrate the investigation workflow.

## Future scope

- Multi-case support (currently hardcoded to one demo case)
- A trained NER model instead of the current regex-based entity extraction
- A properly validated, calibrated risk scoring model developed with domain experts —
  the current scoring is a transparent PoC heuristic, explicitly not a production risk
  assessment tool
- Persistent storage (a real database instead of JSON files) for actual case
  management at scale
- Audit logging of every human review decision
- Role-based access control for multi-investigator teams

## License

MIT — see `LICENSE`.
