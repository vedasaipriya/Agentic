# Multi-Agent QA Assistant — Implementation Plan

Build a local, privacy-safe multi-agent system that ingests Confluence PDFs, clarifies requirements, and generates structured test data — all running offline with a local LLM.

## User Review Required

> [!IMPORTANT]
> **Ollama is NOT installed** on your machine. It's required to run the local LLM. I'll install it as part of Step 1 using `winget install Ollama.Ollama`, then pull a model (`llama3.1:8b` or `mistral:7b`). Please confirm you're okay with this (~4.7 GB download).

> [!IMPORTANT]
> **Model choice**: `llama3.1:8b` is recommended for the best balance of quality and speed on consumer hardware (needs ~8 GB RAM). If your machine has limited resources, `phi3:mini` (~2.3 GB) is a lighter alternative. Which do you prefer?

## Open Questions

1. **Web UI or CLI?** The spec says "Upload PDF" — should I build a web UI (FastAPI + HTML frontend) or a simple CLI tool? I'll default to **web UI with FastAPI** unless you say otherwise.
2. **Confluence PDF specifics**: Do you have a sample PDF I can test with? If not, I'll create a mock requirement PDF for testing.

---

## Architecture Overview

```
e:\Agentic\
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
│   │   ├── base_agent.py        # Base agent class
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
│   ├── sample_requirements.pdf  # Mock Confluence PDF
│   └── test_pipeline.py         # End-to-end test
├── output/                      # Generated JSON outputs
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Local LLM** | Ollama + `llama3.1:8b` | Free, private, no API keys, structured JSON output |
| **LLM Integration** | `langchain-ollama` | Clean Python interface with prompt templates |
| **PDF Parsing** | `pymupdf4llm` | Best-in-class structure preservation (headings, bullets → Markdown) |
| **Backend** | FastAPI + Uvicorn | Async, auto-docs, Pydantic integration |
| **Frontend** | Vanilla HTML/CSS/JS | Lightweight, no build step, premium dark UI |
| **Schema Validation** | Pydantic v2 | Guarantees structured JSON output |
| **Logging** | Python `logging` | Structured, file + console output |

---

## Proposed Changes

### 0. Prerequisites

#### [NEW] Install Ollama
- `winget install Ollama.Ollama` 
- Pull model: `ollama pull llama3.1:8b`
- Verify: `ollama list`

#### [NEW] [requirements.txt](file:///e:/Agentic/requirements.txt)
```
fastapi>=0.115.0
uvicorn>=0.30.0
python-multipart>=0.0.9
pymupdf4llm>=0.0.17
langchain-ollama>=0.2.0
langchain-core>=0.3.0
pydantic>=2.0.0
```

---

### 1. Pydantic Schemas (`app/models/schemas.py`)

#### [NEW] [schemas.py](file:///e:/Agentic/app/models/schemas.py)

Define strict output contracts:

```python
class ClarificationResult(BaseModel):
    summary: str
    missing_requirements: list[str]
    ambiguities: list[str]
    clarification_questions: list[str]
    assumptions: list[str]
    risk_level: str  # "low" | "medium" | "high" | "critical"

class TestDataResult(BaseModel):
    valid_cases: list[dict]
    invalid_cases: list[dict]
    edge_cases: list[dict]
    boundary_values: list[dict]
    security_cases: list[dict]

class PipelineResult(BaseModel):
    pdf_filename: str
    extracted_text: str
    clarification: ClarificationResult
    test_data: TestDataResult
    processing_time_seconds: float
```

---

### 2. PDF Parser Module (`app/pdf_parser/`)

#### [NEW] [extractor.py](file:///e:/Agentic/app/pdf_parser/extractor.py)
- Use `pymupdf4llm.to_markdown()` to extract text preserving headings (`#`, `##`) and bullets (`-`, `*`)
- Returns raw Markdown string

#### [NEW] [cleaner.py](file:///e:/Agentic/app/pdf_parser/cleaner.py)
- Remove Confluence noise: page numbers, headers/footers, "Powered by Confluence" text
- Strip excessive whitespace, fix broken lines
- Detect and preserve requirement sections
- Returns cleaned Markdown string

---

### 3. AI Agents (`app/agents/`)

#### [NEW] [base_agent.py](file:///e:/Agentic/app/agents/base_agent.py)
- Base class with `OllamaLLM` integration
- Handles prompt construction, JSON parsing, retry logic
- Validates output against Pydantic schema
- If LLM returns malformed JSON, retries up to 3 times with error feedback

#### [NEW] [clarifier.py](file:///e:/Agentic/app/agents/clarifier.py)
- System prompt instructs the LLM to act as a Senior QA Requirements Analyst
- Analyzes requirement text for:
  - Missing specifications
  - Ambiguous language
  - Implicit assumptions
  - Risk assessment
- Returns `ClarificationResult`

#### [NEW] [test_generator.py](file:///e:/Agentic/app/agents/test_generator.py)
- System prompt instructs the LLM to act as a Test Data Engineering specialist
- Takes `ClarificationResult` + original text
- Generates:
  - Valid test scenarios with realistic data
  - Invalid inputs (wrong types, formats, boundaries)
  - Edge cases (empty strings, unicode, max-length)
  - Boundary values (min/max, off-by-one)
  - Security cases (SQL injection, XSS, path traversal)
- Returns `TestDataResult`

---

### 4. Orchestrator (`app/orchestrator.py`)

#### [NEW] [orchestrator.py](file:///e:/Agentic/app/orchestrator.py)
- `run_pipeline(pdf_path)` → coordinates the full flow:
  1. Extract text from PDF
  2. Clean text
  3. Run Clarification Agent
  4. Validate output
  5. Run Test Data Generator Agent
  6. Assemble `PipelineResult`
  7. Save JSON to `output/` directory
- Includes timing and error handling

---

### 5. FastAPI Backend (`app/main.py`)

#### [NEW] [main.py](file:///e:/Agentic/app/main.py)
- `POST /api/analyze` — accepts PDF upload, runs pipeline, returns JSON
- `GET /api/health` — health check (verifies Ollama connectivity)
- `GET /` — serves the frontend
- Static file serving for `frontend/`

---

### 6. Frontend (`frontend/`)

#### [NEW] [index.html](file:///e:/Agentic/frontend/index.html)
Premium dark-mode dashboard:
- Drag-and-drop PDF upload zone
- Real-time progress indicators (Processing → Clarifying → Generating)
- Collapsible result cards for each agent output
- JSON download button
- Glassmorphism cards, smooth animations

#### [NEW] [style.css](file:///e:/Agentic/frontend/style.css)
- Dark theme with gradient accents
- Glassmorphism panels
- Micro-animations (fade-in, pulse, progress bars)
- Responsive layout

#### [NEW] [app.js](file:///e:/Agentic/frontend/app.js)
- File upload handling with drag-and-drop
- API communication
- Dynamic result rendering
- Error handling with toast notifications

---

### 7. Logging & Config

#### [NEW] [logger.py](file:///e:/Agentic/app/utils/logger.py)
- Structured logging with timestamps
- File + console handlers
- Log levels: INFO for flow, DEBUG for LLM prompts/responses, ERROR for failures

#### [NEW] [config.py](file:///e:/Agentic/app/config.py)
- Centralized configuration:
  - `OLLAMA_MODEL` (default: `llama3.1:8b`)
  - `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
  - `OUTPUT_DIR`
  - `MAX_RETRIES`

---

### 8. Testing

#### [NEW] [sample_requirements.pdf](file:///e:/Agentic/tests/sample_requirements.pdf)
- Generated mock Confluence PDF with realistic requirements (password reset, user registration, etc.)

#### [NEW] [test_pipeline.py](file:///e:/Agentic/tests/test_pipeline.py)
- End-to-end test: PDF → Clarification → Test Data → Validate JSON

---

## Verification Plan

### Automated Tests
1. `python -m pytest tests/test_pipeline.py` — end-to-end pipeline test
2. `ollama list` — verify model is available
3. `curl http://localhost:11434/api/tags` — verify Ollama is running
4. `curl -X POST http://localhost:8000/api/analyze -F "file=@tests/sample_requirements.pdf"` — API test

### Manual Verification
1. Open `http://localhost:8000` in browser
2. Upload the sample PDF
3. Verify both agent outputs are valid JSON matching the schemas
4. Check `output/` directory for saved results
5. Browser recording of the full upload → results flow

---

## Execution Order

1. Install Ollama & pull model
2. Create `requirements.txt` & install dependencies
3. Build schemas (`models/schemas.py`)
4. Build PDF parser (`pdf_parser/`)
5. Build base agent + both agents (`agents/`)
6. Build orchestrator
7. Build FastAPI backend
8. Build frontend UI
9. Create sample PDF & test
10. End-to-end verification
