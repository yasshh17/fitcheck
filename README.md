<div align="center">

# FitCheck

### AI-Powered Resume & Job Fit Analyzer

**Know your fit. Before you apply.**

[![Python](https://img.shields.io/badge/Python-3.12.6-3776ab?logo=python&logoColor=white)](https://python.org/)
[![Reflex](https://img.shields.io/badge/Reflex-0.9.1-6366f1)](https://reflex.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?logo=openai&logoColor=white)](https://openai.com/)
[![Security](https://img.shields.io/badge/Security-Hardened-22c55e)](https://github.com/yasshh17/fitcheck#security)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

[Live Demo](#running) • [Architecture](#architecture) • [Security](#security) • [Getting Started](#getting-started)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Preview](#preview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Security](#security)
- [AI Integration](#ai-integration)
- [Cost Estimate](#cost-estimate)
- [Limitations](#limitations)
- [Development](#development)
- [License](#license)

---

## Overview

**FitCheck** is a single-page, AI-powered resume analyzer built entirely in Python using [Reflex](https://reflex.dev) -- a full-stack Python framework that compiles to React/Next.js on the frontend and runs a Python/Uvicorn backend. No JavaScript written by hand.

### The Problem

Job seekers apply to dozens of roles without knowing whether their background genuinely matches the requirements:

- Wasted time applying to poor-fit roles
- No actionable feedback on what skills are missing
- No way to quickly compare yourself against a job description

### The Solution

FitCheck uses OpenAI `gpt-4o-mini` to evaluate fit and return:

- A **score (1-10)** showing how well the candidate matches the role
- **3 strengths** -- the specific skills and experiences that match
- **2-3 gaps** -- what the candidate is missing and should address
- A **plain-English recommendation** in 1-2 sentences

```diff
- Traditional: "Am I a good fit?" (guesswork, subjective)
+ FitCheck:    "You're an 8/10. Strong FastAPI and RAG experience.
+               Gap: limited Go background." (scored, specific, actionable)
```

---

## Key Features

- **Fit Score (1-10)** -- color-coded badge: green (7-10), amber (4-6), red (1-3)
- **Strengths, Gaps, Recommendation** -- structured AI output with schema validation
- **Navbar + character counters** -- live `X / 15,000 characters` display per field
- **Colored section cards** -- Strengths (green), Gaps (amber), Recommendation (blue) with icons
- **Rate limiting** -- 5-second cooldown and 50 analyses per session per day
- **Input length cap** -- 15,000 character limit enforced in browser and server
- **Sanitized error handling** -- specific exception handlers per failure type; raw errors never shown to users
- **30-second API timeout** -- no permanently hung spinner
- **Responsive dark theme** -- two-column desktop, stacked mobile; deep navy with electric blue accents

---

## Preview

```
+----------------------------------------------------------+  <- 4px blue top border
| * FitCheck                        AI Resume Analyzer    |  <- navbar
+----------------------------------------------------------+

+-------------------------------+  +----------------------------------+
| JOB DESCRIPTION               |  | [check] Analysis Complete        |
| +-------------------------+   |  |                                  |
| | We are looking for a   |   |  | FIT SCORE                        |
| | Software Engineer with |   |  | +------------------------------+ |
| | Python, FastAPI...     |   |  | |   8          out of 10       | |
| +-------------------------+   |  | +------------------------------+ |
| 313 / 15,000 characters       |  |                                  |
|                               |  | [^] YOUR STRENGTHS               |
| RESUME / CANDIDATE BACKGROUND |  | * FastAPI and LangChain exp.     |
| +-------------------------+   |  | * Proficient Python + SQL        |
| | Software engineer with |   |  | * AWS deployment hands-on        |
| | 1 year production exp. |   |  |                                  |
| | Built FastAPI...       |   |  | [!] GAPS TO ADDRESS              |
| +-------------------------+   |  | * 1 year of experience           |
| 315 / 15,000 characters       |  | * Limited vector DB exposure     |
|                               |  |                                  |
| [ Analyze Fit ]               |  | [*] RECOMMENDATION               |
+-------------------------------+  | Strong candidate. Vector DB      |
                                   | gap is trainable on the job.     |
                                   |                                  |
                                   | [ Analyze Another Role ]         |
                                   +----------------------------------+
```

---

## Architecture

### System Diagram

```
+--------------------------------------------------------------+
|                   BROWSER  (port 3001)                       |
|                                                              |
|   +---------------------+     +--------------------------+  |
|   |    input_panel      |     |     results_panel        |  |
|   |                     |     |                          |  |
|   |  Navbar             |     |  Fit Score badge         |  |
|   |  Job Desc textarea  |     |  Strengths card (green)  |  |
|   |  Resume textarea    |     |  Gaps card (amber)       |  |
|   |  Char counters      |     |  Recommendation (blue)   |  |
|   |  Analyze button     |     |  Reset button            |  |
|   +----------+----------+     +--------------------------+  |
+______________+_______________________________________________+
               |
               |  WebSocket  (managed by Reflex)
               |
+______________v_______________________________________________+
|                PYTHON BACKEND  (port 8000)                   |
|                                                              |
|   +--------------------------------------------------+      |
|   |        FitCheckState  (rx.State subclass)        |      |
|   |                                                  |      |
|   |  job_description  -->  set_job_description()     |      |
|   |  resume_text      -->  set_resume_text()         |      |
|   |  is_loading       -->  analyze_fit()  --------+  |      |
|   |  fit_score             reset_analysis()       |  |      |
|   |  strengths                                    |  |      |
|   |  gaps              Computed vars              |  |      |
|   |  recommendation    score_color           <----+  |      |
|   |  error_message     can_analyze                   |      |
|   |  show_results                                    |      |
|   +--------------------------------------------------+      |
|                     |  OpenAI API  (gpt-4o-mini)            |
|   Uvicorn ASGI      |  JSON response                        |
+_____________________v________________________________________+
               |
+______________v_______________________________________________+
|         REFLEX COMPILER  (build time only)                   |
|   Python components  ->  Next.js / React                     |
+--------------------------------------------------------------+
```

### Data Flow

```
1. User types in textarea
        |
        v
2. on_change fires --> state var updates, char counter refreshes
        |
        v
3. User clicks "Analyze Fit"
        |
        v
4. analyze_fit() validates before any API call:
   |-- both fields non-empty
   |-- each field <= 15,000 characters
   |-- rate limit: 5s cooldown, 50/day cap
   |-- OPENAI_API_KEY present in environment
   |
   |-- Sets is_loading = True
   +-- yield  <-- flushes spinner to browser NOW, before API call
        |
        v
5. AsyncOpenAI calls gpt-4o-mini with 30s timeout
        |
        v
6. JSON parsed and schema validated:
   { fit_score, strengths, gaps, recommendation }
   fit_score clamped 1-10, lists capped at 5 items
        |
        v
7. State updates: show_results=True, is_loading=False
   Reflex WebSocket pushes state to browser
   results_panel re-renders -- no page reload needed
        |
        v
8. On failure, specific exception handler fires:
   APITimeoutError     --> "Request timed out. Please try again."
   AuthenticationError --> "Service authentication error."
   RateLimitError      --> "Service is temporarily busy."
   ParseError          --> "Could not parse the AI response."
   Real error logged to stderr only -- never shown in UI
```

### Key Architectural Decisions

| Decision | Rationale | Trade-off |
|---|---|---|
| Reflex (Python full-stack) | Single codebase, no JS context switch for Python teams | Less mature ecosystem than React + FastAPI |
| Server-side state (rx.State) | Reactive UI without Redux or Zustand | Per-session memory scales linearly with users |
| WebSocket communication | Real-time reactive updates without polling | No stateless CDN caching for app logic |
| gpt-4o-mini | Fast, cheap, sufficient for structured JSON | GPT-4o more accurate at 10x cost |
| Stateless (no DB) | Zero PII storage risk | Results lost on page reload |
| os.environ.get() at call time | Key never in memory at startup; sanitized error on failure | Slightly slower than module-level import |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Full-stack framework | Reflex 0.9.1 |
| AI model | OpenAI gpt-4o-mini |
| Frontend (compiled) | Next.js / React -- managed by Reflex |
| Backend (managed) | Python + Uvicorn ASGI -- managed by Reflex |
| Python runtime | 3.12.6 via pyenv |
| Env management | python-dotenv 1.0.1 |

**3 explicit packages** -- Reflex resolves the rest automatically:

```
reflex~=0.9.1          # Entire framework: frontend + backend + WebSocket
openai~=1.109.0        # OpenAI Python SDK for gpt-4o-mini calls
python-dotenv~=1.0.1   # .env file loading for local development
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Installation

```bash
# Clone the repository
git clone https://github.com/yasshh17/fitcheck.git
cd fitcheck

# Install dependencies
python3 -m pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Open .env and add your real OPENAI_API_KEY
```

```env
OPENAI_API_KEY=sk-...your-key-here...
```

### Running

```bash
# Export the API key into your shell session
# (Reflex does not auto-load .env files)
export $(cat .env | xargs)

# Development (hot-reload, verbose logging, source maps)
python3 -m reflex run

# Production / public demo (no source maps, no hot-reload)
python3 -m reflex run --env prod
```

App runs at **http://localhost:3000** (or 3001 if 3000 is in use).

> **Note:** Run `export $(cat .env | xargs)` every time you open a new terminal.
> Skipping this causes a "Service configuration error" when you click Analyze.

> **Security:** Always use `--env prod` when sharing a public link.

### Verify Installation

```bash
python3 -m pip show reflex
# Expected: Version: 0.9.1
```

---

## Usage

1. Paste a job description into the left textarea
2. Paste your resume or background summary into the second textarea
3. Click **Analyze Fit** -- spinner shows while GPT-4o-mini processes (3-8 seconds)
4. Review results:
   - Green score (7-10) = strong fit; amber (4-6) = marginal; red (1-3) = mismatch
   - Strengths, Gaps, and Recommendation give specific, actionable detail
5. Click **Analyze Another Role** to reset and start over

---

## Project Structure

```
fitcheck/
|-- rxconfig.py                    # Reflex app configuration
|-- requirements.txt               # 3 explicit dependencies (pinned ~=)
|-- requirements-lock.txt          # Full lockfile (pip freeze)
|-- .env                           # Secrets -- NOT committed to git
|-- .env.example                   # Environment variable template
|-- CLAUDE.md                      # Architecture context for AI assistants
|-- README.md                      # This file
+-- app/
    |-- app.py                     # Navbar, page layout, rx.App entry point
    |-- components/
    |   |-- input_panel.py         # Left panel: textareas, counters, button
    |   +-- results_panel.py       # Right panel: score, strengths, gaps
    +-- states/
        +-- fitcheck_state.py      # All state, rate limiting, OpenAI handler
```

---

## How It Works

1. Text inputs are bound to `FitCheckState` via `on_change` handlers. Character counts update live with every keystroke.

2. On click, `analyze_fit()` validates inputs before any API call: non-empty check, 15,000 character cap, rate limit check (5s cooldown, 50/day), and API key presence.

3. The handler sets `is_loading = True` and `yield`s -- this flushes the loading state to the browser **before** the blocking API call. The spinner appears instantly.

4. `AsyncOpenAI` calls `gpt-4o-mini` with a 30-second timeout and a system prompt enforcing strictly valid JSON output with no markdown or code fences.

5. The JSON response is parsed and schema-validated -- all four keys must be present. Output is clamped: score bounded 1-10, lists capped at 5 items, recommendation capped at 1,000 characters.

6. Reflex's WebSocket pushes updated state to the browser. The results panel re-renders automatically -- no page reload.

7. Each failure mode has a specific exception handler returning a sanitized message. Real errors go to `stderr` only.

---

## Security

Full security audit performed across 8 vulnerability categories.

### Protections in Place

| Category | What Is Implemented |
|---|---|
| Secrets | API key via `os.environ.get()` at call time -- never hardcoded or imported at startup |
| Secrets | `.gitignore` covers `.env*` variants -- prevents accidental commits |
| Input validation | 15,000 char limit enforced browser-side (`max_length`) and server-side |
| Rate limiting | 5-second cooldown + 50 analyses per session per day |
| API timeout | 30-second timeout -- no permanently hung spinner |
| Error handling | Specific handlers per OpenAI error type; sanitized UI messages; real errors to `stderr` |
| Response validation | JSON schema validated; `fit_score` clamped 1-10; output lengths capped |
| Dependencies | `~=` version pins + `requirements-lock.txt` for reproducible builds |
| XSS | Not possible -- all output through React's text pipeline (no `dangerouslySetInnerHTML`) |
| SQL injection | Not applicable -- no database; app is fully stateless |
| Data privacy | No database, no file writes; resume data in per-session memory only |

### Audit Summary

| ID | Severity | Finding | Status |
|---|---|---|---|
| A-1 | High | No rate limiting on `analyze_fit()` | Fixed |
| I-1 | High | No maximum input length | Fixed |
| A-2 | Medium | No API call timeout | Fixed |
| A-3 | Medium | Raw exception string shown to user | Fixed |
| S-1 | Medium | OpenAI auth error may expose key details | Fixed |
| I-2 | Medium | No prompt injection defense or schema validation | Fixed |
| D-1 | Medium | Unbounded `>=` version pins | Fixed |
| C-1 | Medium | No production mode documentation | Fixed |
| S-2 | Low | `load_dotenv()` redundant and misleading | Fixed |
| S-3 | Low | `.gitignore` missing `.env.*` variants | Fixed |
| E-1 | Low | `KeyError` leaked env var name to UI | Fixed |
| D-2 | Low | No lockfile | Fixed |
| F-1 | Info | XSS via React escaping | Confirmed safe |
| P-1 | Info | PII storage | Confirmed safe |

### Known Open Items

- No CSP / `X-Frame-Options` headers -- needs a reverse proxy for production hosting
- Reflex telemetry enabled by default (anonymous; no user data)

---

## AI Integration

| Setting | Value |
|---|---|
| Model | `gpt-4o-mini` |
| Temperature | `0.3` -- low for consistent JSON output |
| Timeout | `30.0` seconds |
| API key source | `os.environ.get("OPENAI_API_KEY")` at call time |

**Required JSON schema:**

```json
{
  "fit_score": 8,
  "strengths": ["string", "string", "string"],
  "gaps": ["string", "string"],
  "recommendation": "1-2 sentence string"
}
```

---

## Cost Estimate

| | Tokens |
|---|---|
| Input (system prompt + job description + resume) | ~300-500 tokens |
| Output (JSON response) | ~150-200 tokens |
| **Cost per analysis** | **Under $0.01** |

---

## Limitations

- Input capped at **15,000 characters** per field
- **50 analyses per session per day** with a 5-second cooldown between requests
- Results are **not persisted** -- resets on page reload
- No user authentication -- rate limit is per-session, not per account

---

## Development

### Adding a State Variable

```python
class FitCheckState(rx.State):
    new_var: str = ""

    def set_new_var(self, value: str):   # Explicit setter required in Reflex 0.9
        self.new_var = value
```

### Dependency Management

```bash
# Reproducible install from lockfile
pip install -r requirements-lock.txt

# Regenerate lockfile after adding packages
python3 -m pip freeze > requirements-lock.txt
```

---

## License

MIT -- free to use, modify, and distribute.

---

## Contact

**Yash Tambakhe**

[![GitHub](https://img.shields.io/badge/GitHub-yasshh17-181717?style=for-the-badge&logo=github)](https://github.com/yasshh17)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Yash_Tambakhe-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/yash-tambakhe/)
[![Email](https://img.shields.io/badge/Email-yashtambakhe@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:yashtambakhe@gmail.com)

- **Portfolio:** [yashtambakhe.com](https://yashtambakhe.com)
- **Source:** [github.com/yasshh17/fitcheck](https://github.com/yasshh17/fitcheck)

---

<div align="center">

**Built by [Yash Tambakhe](https://github.com/yasshh17)**

*Full-stack Python AI -- Reflex 0.9.1 + OpenAI gpt-4o-mini*

</div>