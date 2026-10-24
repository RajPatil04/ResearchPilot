# 🔬 ResearchPilot AI
### *Understand research beyond the abstract — powered by Gemma 4.*

[![Hackathon: Best Use of Gemma 4](https://img.shields.io/badge/Hackathon-Best%20Use%20of%20Gemma%204-6366f1.svg)](https://ai.google.dev/gemma)
[![Model: Gemma 4](https://img.shields.io/badge/Gemma%204-gemma--4--26b--a4b--it-0284c7.svg)](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api)
[![Frontend: React + Vite](https://img.shields.io/badge/Frontend-React%2019%20%2B%20TypeScript%20%2B%20Tailwind-61dafb.svg)](https://react.dev/)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI%20REST%20%2B%20SSE-009688.svg)](https://fastapi.tiangolo.com/)
[![SDK: Google Gen AI](https://img.shields.io/badge/SDK-Google%20Gen%20AI%20Python-10b981.svg)](https://pypi.org/project/google-genai/)
[![Tests: 35 Passing](https://img.shields.io/badge/Tests-35%20Passed-34d399.svg)](#testing-instructions)

---

## 📌 Project Overview & Problem Statement

Scientific literature is expanding at over 3 million published papers per year. Graduate students, academic researchers, and engineers spend up to 40% of their research time wading through dense prose, locating methodology parameters, parsing complex diagrams, and validating quantitative baselines.

Conventional AI summarizers frequently suffer from critical flaws:
1. **Hallucination of Metrics:** Inventing baseline numbers, p-values, or dataset sizes.
2. **Ungrounded Claims:** Presenting speculation as factual findings without page citations.
3. **Inability to Read Diagrams:** Treating papers as plain text while ignoring architectural flowcharts and loss plots.
4. **Silent Substitution:** Many apps silently fall back to alternative models when target endpoints fail, masking availability realities.

**ResearchPilot AI** solves this by delivering an evidence-grounded research assistant powered strictly by **Gemma 4** through the Gemini API. Every claim is tied to explicit `[PAGE N]` citations, limitations are segregated from hypotheses, charts are inspected multimodally, and an autonomous research agent investigates queries using registered inspection tools.

The interface is built as a **ChatGPT-style research assistant** featuring a compact left sidebar, central multi-turn chat area with quick-prompt chips, a bottom-anchored composer with a `+` research tools popup, and a collapsible right-side source citations panel.

---

## 🚀 Key Features & Interface Layout

### 🎨 1. Modern ChatGPT-Style Research Workspace
- **Compact Left Sidebar:**
  - **New Chat** button to start fresh inquiry threads.
  - **Paper Library:** Drag-and-drop PDF upload zone, quick sample paper loader, and click-to-switch active paper selector.
  - **Workspace Metrics:** Live counts for active papers, indexed pages, and total words.
  - **Recent Conversations:** Switch between past research sessions.
  - **Settings Button:** Easy access to API key and model controls.
- **Top Header Bar:**
  - **Paper Scope Indicator:** Displays active paper title, page count, and word count.
  - **Gemma 4 Badge:** Model pill showing `gemma-4-26b-a4b-it`.
  - **Connection Status Pill:** Live indicator (`Connected` vs. `Not Configured`).
  - **Sources Toggle:** Quick toggle to expand or collapse the right-hand citations panel.
  - **Settings Button:** Direct shortcut to connection modal.
- **Central Conversation Area:**
  - **Welcome Hero:** Four quick-start research prompts (*"Summarize core contribution"*, *"Extract experimental baselines"*, *"Explain theoretical methodology"*, *"Analyze limitations & risks"*).
  - **Rich Markdown Formatting:** Tables, mathematical equations, and syntax-highlighted code blocks.
  - **Interactive Citation Badges:** Clickable `[PAGE N]` and `SR-` badge pills highlighting referenced pages.
  - **Action Controls:** One-click copy response and download individual markdown notes.
  - **Streaming Feedback:** Visual SSE indicator during Gemma 4 inference.
- **Bottom-Anchored Composer:**
  - **Auto-Resizing Input:** Multi-line textarea that expands cleanly with user input.
  - **Paper Attachment Chip:** Visual indicator of active paper scope with quick remove button.
  - **`+` Research Tools Popup Menu:**
    - 📑 **Full Summary:** Generates the 12-section structured research breakdown.
    - 🧭 **Research Insights:** Generates 5-section limitation analysis and 3–5 proposed research directions.
    - 🖼️ **Figure Vision:** Multimodal visual diagram and chart inspection.
    - 🤖 **Autonomous Agent:** Launches multi-step tool investigation with live execution trace.
  - **Send / Stop Controls:** Instant submission with keyboard shortcuts (`Enter` to send, `Shift+Enter` for new line).
- **Collapsible Right-Side Source Panel:**
  - Collapsed by default to maximize conversation reading width.
  - **Active Paper Scope:** Indexed pages, lexical density, and section outline.
  - **Verified Source Citations:** Card-based citations (`SR-1`, `SR-2`) showing exact page numbers and verbatim quoted text snippets.

---

### 📑 2. Structured Research Summarization
- Generates a comprehensive 12-section scientific breakdown: Paper title, plain-language executive overview, research problem & motivation, objectives, methodology & architectures, datasets & data sources, experimental setup & baselines, key findings with exact metrics, conclusion, explicit limitations, important terminology explained simply, and an evidence page index.
- Strict anti-hallucination constraint: If a metric or dataset is missing, writes `"Not specified in the provided text."`

### 💬 3. Grounded "Ask the Paper" Multi-Turn Chat
- Interactive dialogue preserving session conversation history.
- Smart lexical page retrieval injects relevant page passages so even long papers receive grounded answers.
- Citations with `[PAGE N]` labels for every factual assertion.
- Distinguishes author-stated paper facts from general background context.

### 🧭 4. Research Insights & Opportunity Discovery
- **Section A:** Explicitly reported limitations directly quoted with page citations.
- **Section B:** Inferred limitations labeled as `[Model Inference - Not stated by authors]`.
- **Section C:** 3 to 5 actionable research directions, each complete with:
  - Research question
  - Motivation and tie to the paper
  - Proposed methodology
  - Suggested experiment, datasets, and baselines
  - Specific evaluation metrics
  - Anticipated challenges
  - Evidence that would support or refute the hypothesis
- **Section D:** Author-proposed future work (kept strictly distinct).
- **Section E:** Research reliability and evidence assessment.

### 🖼️ 5. Multimodal Figure, Chart & Diagram Analysis
- Renders any selected PDF page to high-resolution PNG bytes using PyMuPDF.
- Gemma 4 visually inspects architecture flowcharts, scatter plots, loss curves, and comparison tables.
- Identifies axes, units, legends, and inflection points.
- Acknowledges unreadable labels honestly rather than guessing missing numbers.

### 🤖 6. Agentic Research Assistant (Autonomous Tools)
- Autonomous research agent that plans evidence gathering and executes registered, read-only tools:
  - `get_paper_metadata`: Extracts title, page count, word count, and detected sections.
  - `get_page_text`: Retrieves full text of any 1-indexed page with bounds validation.
  - `search_paper_text`: Performs lexical relevance search across the paper's index.
  - `get_paper_statistics`: Analyzes structural density and word distribution.
  - `render_pdf_page`: Renders page images for visual reasoning.
- Safe execution: strictly registered functions only; no arbitrary code, shell commands, or file system access.
- Interactive execution trace displays every tool call, argument, and output step.

### 📥 7. Export Center & Research Dossier
- Export individual reports: Summary (`.md`), Chat Transcript (`.md`), Research Insights (`.md`), and Figure Notes (`.md`).
- **Complete Research Dossier (`.md`):** Consolidates all generated artifacts, metadata, timestamps, and model parameters into a single publication-ready Markdown file.

---

## 🏛️ System Architecture

```mermaid
graph TD
    User([User / Researcher]) -->|Interacts| ReactUI[React 19 + TypeScript + Vite Frontend]
    
    subgraph Frontend [Modern Single-Page Client]
        ReactUI --> Sidebar[Sidebar: Papers & Conversations]
        ReactUI --> ChatArea[ChatGPT Conversation Area]
        ReactUI --> Composer[Composer with '+' Research Tools Menu]
        ReactUI --> SourcePanel[Collapsible Citations & Scope Panel]
        ReactUI --> Modals[Summary / Insights / Figure / Agent Modals]
    end

    subgraph Backend [FastAPI REST + SSE Engine]
        ReactUI -->|REST / SSE API| FastAPIApp[FastAPI Application]
        FastAPIApp --> StateMgr[State Manager & Memory Index]
        FastAPIApp --> PDFProc[PDFProcessor - PyMuPDF]
        FastAPIApp --> AgentEngine[ResearchAgent - Safe Tool Registry]
        FastAPIApp --> ExportEng[Export Center & Dossier Generator]
    end

    subgraph Local PDF Engine [In-Memory Local Processing]
        PDFProc --> PageIndexer[Page-by-Page Indexer [PAGE N]]
        PDFProc --> LexicalSearch[Lexical Relevance Search Engine]
        PDFProc --> PageRenderer[High-Res Page Renderer to PNG]
    end

    subgraph Gemma 4 Integration [Google Gen AI SDK]
        FastAPIApp --> Client[GemmaClient]
        Client -->|Strict Model Targeting| GemmaModel[(gemma-4-26b-a4b-it)]
        Prompts[Grounded Prompts & System Instructions] --> Client
        PageRenderer -->|PNG Bytes| Client
        LexicalSearch -->|Grounded Context| Client
    end
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend UI** | React 19, TypeScript, Vite 8, Tailwind CSS v4, Lucide React | Modern, ChatGPT-style scientific research workspace |
| **Backend API** | FastAPI, Uvicorn, Starlette, Pydantic | High-performance async REST endpoints and SSE streaming |
| **Model** | **Gemma 4** (`gemma-4-26b-a4b-it`) | Reasoning, structured summarization, multimodal vision, and Q&A |
| **AI SDK** | `google-genai` (2.33+) | Official Google Gen AI Python SDK |
| **PDF Extraction** | PyMuPDF (`pymupdf` 2.0+) | Local text extraction, page boundary indexing, and image rendering |
| **Data & Types** | Python 3.12 Standard Library, Pillow, Pydantic | Cross-platform utilities, safe tool validation |
| **Testing** | Python `unittest` | 35 automated unit tests covering processing, prompts, agent tools, client mocks, and API endpoints |
| **Legacy UI** | Streamlit 1.66+ | Preserved as a standalone secondary interface (`app.py`) |

---

## 🔌 Gemma 4 API Integration Details

ResearchPilot AI follows the official [Gemma on Gemini API documentation](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api):
- **Default Model Identifier:** `gemma-4-26b-a4b-it` (configurable via `GEMMA_MODEL` environment variable or UI selector).
- **Secondary Model Support:** `gemma-4-31b-it` and custom model identifier input.
- **Strict Model Fidelity:** The application **never silently substitutes** Gemini 2.5, Gemini 3, GPT, or Claude when a Gemma request fails. If an error occurs, the actual API message is displayed with clear remediation instructions.
- **System Instructions:** Configured via `types.GenerateContentConfig(system_instruction=...)` enforcing strict scientific anti-hallucination rules.
- **Thinking Configuration:** Configurable toggle setting `types.ThinkingConfig(thinking_level="high")` for complex reasoning queries.
- **Multimodal Visual Input:** Rendered PDF pages are sent directly via `types.Part.from_bytes(data=image_bytes, mime_type="image/png")`.
- **API Key Security:** Key is read from `GEMINI_API_KEY` or masked password input. Raw keys are automatically stripped from error logs, never displayed in frontend state, and never committed.

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Node.js 18+ and npm
- A Google AI Studio API Key ([Get one here](https://aistudio.google.com/))
- Standard Windows, macOS, or Linux machine (no GPU required)

---

### Option A: Single-Command Production Launch (Recommended)

FastAPI automatically serves the pre-built React production frontend at `http://localhost:8000`.

```powershell
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Run the application launcher
python run_app.py
```

*The launcher starts the server and automatically opens `http://localhost:8000` in your default browser.*

---

### Option B: Full-Stack Development Mode

Run the FastAPI backend with hot reloading alongside the Vite development server with instant HMR:

**Terminal 1 — Backend (FastAPI):**
```powershell
.venv\Scripts\activate
uvicorn backend.app.main:app --reload --port 8000
```

**Terminal 2 — Frontend (Vite + React):**
```powershell
cd frontend
npm run dev
```

*Open `http://localhost:5173` in your browser. All API requests are automatically proxied to the backend on port 8000.*

---

### Option C: Legacy Streamlit UI

The original Streamlit interface is preserved for users who prefer the multi-tab layout:

```powershell
.venv\Scripts\activate
streamlit run app.py
```

---

## 🧪 Testing Instructions

ResearchPilot AI includes a comprehensive, self-contained test suite that runs **locally without requiring a live API key** using synthetic in-memory PDFs and mock SDK clients.

To execute all 35 automated unit tests:

```bash
# Run the complete test suite
python -m unittest discover tests -v
```

### Test Coverage Summary (35 Tests Passing):
- `tests/test_pdf_processor.py` (7 tests): Valid text extraction, boundary preservation, title detection, section identification, empty bytes handling, scanned PDF / OCR detection, page rendering, lexical search, and budget construction.
- `tests/test_prompts.py` (5 tests): System instruction anti-hallucination rules, 12-section summary structure, conversation history QA formatting, 5-section research insights structure, and figure inspection prompt.
- `tests/test_agent.py` (5 tests): Safe execution of all 5 registered tools, rejection of unauthorized shell/file commands, page bounds validation, and trace logging.
- `tests/test_export_utils.py` (5 tests): Filename sanitization, summary export, chat transcript export, insights export, and comprehensive dossier compilation.
- `tests/test_gemma_client_mock.py` (6 tests): Client initialization, masked key formatting, connection testing, text generation, multimodal image generation, and secret key redaction in error messages.
- `tests/test_api.py` (7 tests): Health check, models list, connection validation, document upload & sample loading, conversation state management, agent tool execution endpoint, and file export formatting.

---

## 📋 Manual Integration Test Checklist (Live Gemma 4 Key)

| Step | Action | Expected Result |
|---|---|---|
| **1. Connection Setup** | Click **Settings** (gear icon) in sidebar or header, enter API key, and click **Test Connection**. | Status updates to `Connected` with model `gemma-4-26b-a4b-it`. Key is masked and never exposed. |
| **2. Document Ingestion** | In sidebar, click **Load Sample Paper** (or drag & drop your PDF). | Active document updates; pages, words, and sections are indexed locally. Paper attachment chip appears in composer. |
| **3. Grounded Chat** | Click a prompt chip like *"Summarize core contribution"* or type a query in the bottom composer. | Response streams in with formatted Markdown, code/tables, and clickable `[PAGE N]` and `SR-` citation pills. |
| **4. Source Citations Panel** | Click the **Sources** toggle button in the top header. | Right panel opens displaying active paper metadata, section outline, and verified `SR-1`, `SR-2` page citation cards with snippets. |
| **5. Structured Summary** | In composer, click **`+`** and select **📑 Full Summary**. | 12-section scientific breakdown modal opens with exact metrics, plain-language summary, and markdown download button. |
| **6. Research Insights** | In composer, click **`+`** and select **🧭 Research Insights**. | 5-section modal opens displaying explicit limitations and 3–5 proposed research directions with baselines. |
| **7. Figure Vision** | In composer, click **`+`** and select **🖼️ Figure Vision**, select a page, and click **Analyze Page**. | High-resolution rendered page renders alongside Gemma 4's multimodal analysis of diagrams, axes, and metrics. |
| **8. Autonomous Agent** | In composer, click **`+`** and select **🤖 Autonomous Agent**, enter an inquiry, and click **Investigate**. | Agent executes registered tools with live execution trace showing tool calls, inputs, and synthesized findings. |
| **9. Research Dossier Export** | Inside any modal or message, click the **Export / Download** button. | Clean, formatted Markdown report or full Research Dossier downloaded directly to disk. |

---

## 🔒 Security, Privacy & Safety Considerations

- **No Remote Document Storage:** Uploaded PDFs are parsed purely in-memory using local PyMuPDF. Raw PDF files are never sent to external servers.
- **Selective API Transmission:** Only extracted text passages relevant to active operations and selected rendered page images are sent to the Gemini API.
- **API Key Protection:** Keys are stored in volatile session state only. No keys are written to disk, and all exception handlers sanitize outputs using regex redaction.
- **Safe Agent Tool Sandbox:** The autonomous research agent can only execute 5 hardcoded, read-only Python functions. It has no access to arbitrary Python execution, shell commands, network requests, or the local filesystem.

---

## ⚠️ Important Limitations

1. **Scanned PDFs:** The current version supports digital text-based PDFs. Scanned image-only PDFs require an OCR preprocessing step.
2. **Context Length Budget:** Very long papers (e.g. > 100 pages) are managed through intelligent lexical retrieval; the full document text is not sent in a single prompt to respect token budgets.
3. **Verification Obligation:** LLM-generated summaries and research suggestions should always be cross-referenced with the original paper.

---

## 🔮 Future Improvements

- [ ] Client-side Tesseract / EasyOCR integration for scanned archival PDFs.
- [ ] Embedding-based semantic vector search in addition to lexical retrieval.
- [ ] Direct BibTeX export for cited papers and related work.
- [ ] Side-by-side interactive PDF page viewer with text highlighting.

---

## 🏆 Hackathon Submission Notes: Best Use of Gemma 4

- **Why Gemma 4?** ResearchPilot AI leverages Gemma 4's lightweight yet state-of-the-art open-weights architecture, combining concise reasoning, multimodal image understanding, and structured instruction-following.
- **Uncompromised Fidelity:** Unlike wrappers that substitute proprietary models upon failure, ResearchPilot AI is built specifically for and strictly accesses Gemma 4.
- **Full-Stack Polish:** From local PDF parsing to agentic tool traces, ChatGPT-style composer, and dossier compilation, ResearchPilot AI delivers a production-grade scientific workspace.
