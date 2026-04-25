# 🤖 Agentic — Multi-Agent QA Assistant

A **local, privacy-safe** multi-agent system that processes Confluence PDF documents to generate structured QA insights. Runs entirely offline with a local LLM — no external API calls.

---

## 🎯 What It Does

1. **Upload** a Confluence-exported PDF
2. **Extract & clean** requirement text (preserving headings, bullets, structure)
3. **Agent 1 — Requirement Clarifier**: Identifies missing requirements, ambiguities, risks, and generates clarification questions
4. **Agent 2 — Test Data Generator**: Produces valid, invalid, edge-case, boundary, and security test data
5. **Output** structured JSON results via a premium web dashboard

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Dashboard                         │
│              (Drag & Drop PDF Upload)                    │
└──────────────────────┬──────────────────────────────────┘
                       │ POST /api/analyze
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│                  (app/main.py)                           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   Orchestrator                           │
│               (app/orchestrator.py)                      │
│                                                         │
│   ┌─────────────┐   ┌──────────────┐   ┌────────────┐  │
│   │ PDF Parser  │──▶│  Agent 1:    │──▶│  Agent 2:  │  │
│   │ (Extract &  │   │  Requirement │   │  Test Data │  │
│   │  Clean)     │   │  Clarifier   │   │  Generator │  │
│   └─────────────┘   └──────────────┘   └────────────┘  │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │              Ollama (Local LLM)                 │   │
│   │            llama3.1:8b — Fully Offline           │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
Agentic/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app & routes
│   ├── config.py                # App configuration
│   ├── orchestrator.py          # Workflow coordinator
│   ├── pdf_parser/
│   │   ├── __init__.py
│   │   ├── extractor.py         # PDF text extraction (pymupdf4llm)
│   │   └── cleaner.py           # Text cleaning & noise removal
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py        # Base agent class with retry logic
│   │   ├── clarifier.py         # Requirement Clarification Agent
│   │   └── test_generator.py    # Test Data Generator Agent
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic models for structured output
│   └── utils/
│       ├── __init__.py
│       └── logger.py            # Structured logging
├── frontend/
│   ├── index.html               # Upload UI & results dashboard
│   ├── style.css                # Premium dark-mode styling
│   └── app.js                   # Frontend logic
├── tests/
│   ├── sample_requirements.pdf  # Mock Confluence PDF for testing
│   └── test_pipeline.py         # End-to-end test
├── output/                      # Generated JSON outputs
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Local LLM** | Ollama + `llama3.1:8b` | Free, private, no API keys, structured JSON output |
| **LLM Integration** | `langchain-ollama` | Clean Python interface with prompt templates |
| **PDF Parsing** | `pymupdf4llm` | Best-in-class structure preservation (headings, bullets → Markdown) |
| **Backend** | FastAPI + Uvicorn | Async, auto-docs, Pydantic integration |
| **Frontend** | Vanilla HTML/CSS/JS | Lightweight, no build step, premium dark UI |
| **Schema Validation** | Pydantic v2 | Guarantees structured JSON output |
| **Logging** | Python `logging` | Structured, file + console output |

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **Ollama** installed and running:
   ```bash
   # Install Ollama (Windows)
   winget install Ollama.Ollama

   # Pull the model (~4.7 GB)
   ollama pull llama3.1:8b

   # Verify it's running
   ollama list
   ```

### Installation

```bash
# Clone the repo
git clone https://github.com/vedasaipriya/Agentic.git
cd Agentic

# Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser, upload a PDF, and view the results!

---

## 📄 Agent Outputs

### Agent 1: Requirement Clarification

```json
{
  "summary": "Analysis of password reset feature requirements",
  "missing_requirements": [
    "No specification for password complexity rules",
    "Missing timeout duration for reset links"
  ],
  "ambiguities": [
    "'User can reset password' — which authentication method?"
  ],
  "clarification_questions": [
    "Should the reset link expire? If so, after how long?",
    "Is email the only verification channel, or is SMS supported?"
  ],
  "assumptions": [
    "User must have a verified email address on file"
  ],
  "risk_level": "medium"
}
```

### Agent 2: Test Data Generation

```json
{
  "valid_cases": [
    { "scenario": "Valid email format", "input": "user@company.com", "expected": "Reset email sent" }
  ],
  "invalid_cases": [
    { "scenario": "Invalid email format", "input": "user@@.com", "expected": "Validation error" }
  ],
  "edge_cases": [
    { "scenario": "Empty email field", "input": "", "expected": "Required field error" }
  ],
  "boundary_values": [
    { "scenario": "Max-length email (254 chars)", "input": "a]@b...com", "expected": "Accepted" }
  ],
  "security_cases": [
    { "scenario": "SQL injection in email", "input": "' OR 1=1--@test.com", "expected": "Input sanitized" }
  ]
}
```

---

## 🔄 Pipeline Workflow

```
PDF Upload → Extract Text → Clean & Structure → Agent 1 (Clarify)
    → Validate JSON → Agent 2 (Test Data) → Final JSON Output
```

1. **PDF Processing**: Extract text using `pymupdf4llm`, preserving Markdown structure
2. **Cleaning**: Remove Confluence noise (headers, footers, page numbers)
3. **Clarification**: LLM analyzes requirements for gaps and risks
4. **Validation**: Pydantic ensures output matches schema; retries on failure (up to 3x)
5. **Test Generation**: LLM creates comprehensive test data sets
6. **Output**: JSON saved to `output/` and displayed in dashboard

---

## 🧱 Design Principles

- **Privacy-first**: Everything runs locally — no data leaves your machine
- **Modular**: Each component is independently testable and replaceable
- **Structured output**: Pydantic schemas enforce JSON contracts
- **Resilient**: Retry logic with error feedback for LLM responses
- **Production-ready**: Logging, error handling, health checks

---

## 🚫 Constraints

- ✅ Fully local — no external API calls
- ✅ Supports PDF input
- ✅ Modular architecture
- ✅ Structured JSON output
- ✅ Clean separation between preprocessing and agents
- ❌ No hardcoded responses
- ❌ No monolithic code

---

## 📜 License

Internal enterprise use.
