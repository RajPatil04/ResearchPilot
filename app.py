"""ResearchPilot AI — Advanced AI Research Workspace.

An evidence-grounded research assistant powered strictly by Gemma 4.
Redesigned with a modern, professional Research RAG workspace interface.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional
import streamlit as st

from src.pdf_processor import PDFProcessor, PDFProcessingError
from src.gemma_client import (
    GemmaClient,
    GemmaClientError,
    DEFAULT_GEMMA_MODEL,
    AVAILABLE_GEMMA_MODELS,
)
from src import prompts
from src.research_agent import ResearchAgent
from src.export_utils import (
    export_summary_markdown,
    export_chat_markdown,
    export_insights_markdown,
    export_figure_analysis_markdown,
    export_complete_dossier_markdown,
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ResearchPilot AI — Advanced Research Workspace",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Professional Research Workspace Custom CSS
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Root palette: Dark Navy Research SaaS */
:root {
    --bg-main: #080d1a;
    --bg-sidebar: #0e1528;
    --bg-panel: #111b30;
    --bg-elevated: #17243a;
    --border-color: #26344d;
    --border-focus: #3b82f6;
    --primary-blue: #2563eb;
    --bright-accent: #3b82f6;
    --cyan-accent: #38bdf8;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --badge-bg: rgba(37, 99, 235, 0.15);
}

/* Base application styling */
.stApp {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
}

/* Layout container constraints */
.block-container {
    max-width: 1400px;
    padding-top: 1rem;
    padding-bottom: 2.5rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
}

/* Top Horizontal Header Bar */
.top-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(180deg, #111b30 0%, #0d1527 100%);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 0.75rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
}
.header-left {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}
.header-icon-box {
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
    border: 1px solid #38bdf8;
    width: 38px;
    height: 38px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
}
.header-titles {
    display: flex;
    flex-direction: column;
}
.header-title-text {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.01em;
    line-height: 1.2;
}
.header-subtitle-text {
    font-size: 0.78rem;
    color: var(--cyan-accent);
    font-weight: 500;
}
.header-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

/* Status Badges */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    border: 1px solid transparent;
}
.status-connected {
    background: rgba(34, 197, 94, 0.12);
    border-color: #22c55e;
    color: #4ade80;
}
.status-warning {
    background: rgba(245, 158, 11, 0.12);
    border-color: #f59e0b;
    color: #fbbf24;
}
.status-error {
    background: rgba(248, 113, 113, 0.12);
    border-color: #f87171;
    color: #f87171;
}
.status-ready {
    background: rgba(56, 189, 248, 0.12);
    border-color: #38bdf8;
    color: #38bdf8;
}
.dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
}
.dot-green { background-color: #4ade80; box-shadow: 0 0 6px #4ade80; }
.dot-amber { background-color: #fbbf24; box-shadow: 0 0 6px #fbbf24; }
.dot-red { background-color: #f87171; box-shadow: 0 0 6px #f87171; }
.dot-cyan { background-color: #38bdf8; box-shadow: 0 0 6px #38bdf8; }

/* Navigation Container */
.nav-pill-bar {
    display: flex;
    gap: 0.4rem;
    background: #0d1527;
    border: 1px solid var(--border-color);
    padding: 0.35rem;
    border-radius: 10px;
    margin-bottom: 1.2rem;
    overflow-x: auto;
}

/* Panel Containers */
.workspace-panel {
    background: var(--bg-panel);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}
.panel-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(38, 52, 77, 0.6);
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
}
.panel-title {
    font-size: 0.95rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--cyan-accent);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
}
.panel-subtitle {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* AI Synthesis Panel */
.synthesis-card {
    background: linear-gradient(180deg, #111b30 0%, #0d1527 100%);
    border: 1px solid #2d3e5e;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
.synthesis-meta-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid #1e293b;
}
.meta-chip {
    background: #17243a;
    border: 1px solid #2d3e5e;
    color: #94a3b8;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
}
.meta-chip-blue {
    border-color: #38bdf8;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.08);
}

/* Citations & Document Cards */
.doc-card {
    background: #0d1527;
    border: 1px solid var(--border-color);
    border-radius: 9px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.65rem;
    transition: all 0.2s ease;
}
.doc-card.active {
    border-color: var(--bright-accent);
    background: linear-gradient(180deg, #13203b 0%, #0d1527 100%);
}
.doc-card-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.3rem;
}
.doc-card-meta {
    font-size: 0.76rem;
    color: var(--text-muted);
}

.citation-card {
    background: #0d1527;
    border: 1px solid #26344d;
    border-left: 3px solid #38bdf8;
    border-radius: 8px;
    padding: 0.75rem 0.95rem;
    margin-bottom: 0.75rem;
    transition: transform 0.15s ease;
}
.citation-card:hover {
    border-color: #38bdf8;
    transform: translateY(-1px);
}
.citation-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}
.citation-id {
    font-size: 0.72rem;
    font-weight: 700;
    background: rgba(56, 189, 248, 0.15);
    color: #38bdf8;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
}
.citation-loc {
    font-size: 0.74rem;
    color: #94a3b8;
    font-weight: 500;
}
.citation-body {
    font-size: 0.8rem;
    color: #cbd5e1;
    line-height: 1.45;
    font-style: italic;
    background: rgba(15, 23, 42, 0.6);
    padding: 0.45rem 0.65rem;
    border-radius: 6px;
    border: 1px dashed rgba(56, 189, 248, 0.2);
}

/* Sidebar workspace statistics card */
.stat-box {
    background: #0d1527;
    border: 1px solid var(--border-color);
    border-radius: 9px;
    padding: 0.75rem;
    margin-top: 0.5rem;
}
.stat-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    padding: 0.25rem 0;
    border-bottom: 1px solid rgba(38, 52, 77, 0.4);
}
.stat-row:last-child {
    border-bottom: none;
}
.stat-label {
    color: var(--text-secondary);
}
.stat-value {
    color: var(--cyan-accent);
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    border: 1px solid #3b82f6 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: #111b30 !important;
    border: 1px solid #26344d !important;
    color: #cbd5e1 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
}

/* Text Inputs & Area */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #0d1527 !important;
    color: #f1f5f9 !important;
    border: 1px solid #26344d !important;
    border-radius: 8px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}

/* Metric Widgets */
div[data-testid="stMetric"] {
    background: #0d1527 !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 0.65rem 0.85rem !important;
}
div[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
}
div[data-testid="stMetricValue"] {
    color: var(--cyan-accent) !important;
    font-weight: 700 !important;
    font-size: 1.3rem !important;
}

/* Hide Streamlit default clutter where appropriate */
header[data-testid="stHeader"] {
    background: transparent !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session State Initialization & Workspace Management
# ---------------------------------------------------------------------------
def init_session_state():
    # Workspaces dictionary holding collection of papers
    if "workspaces" not in st.session_state:
        st.session_state["workspaces"] = {
            "Machine Learning": {"papers": {}, "active": None},
            "Biology Research": {"papers": {}, "active": None},
            "NLP Papers": {"papers": {}, "active": None},
            "Default": {"papers": {}, "active": None},
        }

    defaults = {
        "active_workspace": "Machine Learning",
        "active_nav": "Explorer",
        "pdf_processor": None,
        "summary": None,
        "chat_history": [],
        "insights": None,
        "figure_notes": [],
        "agent_reports": [],
        "connection_status": None,
        "last_tested_model": None,
        "last_query": "",
        "last_synthesis": None,
        "last_query_duration": None,
        "last_citations": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()

current_ws_name = st.session_state["active_workspace"]
current_ws_data = st.session_state["workspaces"].get(current_ws_name, {"papers": {}, "active": None})
workspace_papers = current_ws_data["papers"]


# ---------------------------------------------------------------------------
# Helper: Set / Switch Active Document
# ---------------------------------------------------------------------------
def set_active_document(filename: str):
    if filename in workspace_papers:
        current_ws_data["active"] = filename
        st.session_state["pdf_processor"] = workspace_papers[filename]


# Auto-sync active document if processor is set
if st.session_state["pdf_processor"] is None and current_ws_data.get("active"):
    active_fname = current_ws_data["active"]
    if active_fname in workspace_papers:
        st.session_state["pdf_processor"] = workspace_papers[active_fname]


# ---------------------------------------------------------------------------
# TOP HEADER COMPONENT
# ---------------------------------------------------------------------------
def render_top_header(api_key: str, model_id: str):
    # Determine actual connection status
    status_class = "status-ready"
    status_dot = "dot-cyan"
    status_text = f"Gemma 4 Configured ({model_id})"

    if not api_key:
        status_class = "status-warning"
        status_dot = "dot-amber"
        status_text = "API Key Required"
    elif st.session_state.get("connection_status"):
        succ, _ = st.session_state["connection_status"]
        if succ:
            status_class = "status-connected"
            status_dot = "dot-green"
            status_text = f"Gemma 4 Connected ({model_id})"
        else:
            status_class = "status-error"
            status_dot = "dot-red"
            status_text = "Model Connection Failed"

    header_html = f"""
    <div class="top-header-bar">
        <div class="header-left">
            <div class="header-icon-box">🔬</div>
            <div class="header-titles">
                <span class="header-title-text">ResearchPilot AI</span>
                <span class="header-subtitle-text">Advanced AI Research Analysis • Powered by Gemma 4</span>
            </div>
        </div>
        <div class="header-right">
            <div class="status-pill {status_class}">
                <span class="dot {status_dot}"></span>
                <span>{status_text}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SIDEBAR: Workspaces, Documents, API Setup & Statistics
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔬 ResearchPilot AI")
    st.caption("AI Research Workspace Powered by **Gemma 4**")
    st.markdown("---")

    # --- 1. WORKSPACES SECTION ---
    st.markdown("#### 📂 Research Workspaces")
    available_ws = list(st.session_state["workspaces"].keys())
    selected_ws = st.selectbox(
        "Active Workspace",
        available_ws,
        index=available_ws.index(current_ws_name) if current_ws_name in available_ws else 0,
        help="Switch research workspaces to organize paper collections.",
    )
    if selected_ws != current_ws_name:
        st.session_state["active_workspace"] = selected_ws
        # Update active document reference to this workspace
        new_ws = st.session_state["workspaces"][selected_ws]
        active_f = new_ws.get("active")
        st.session_state["pdf_processor"] = new_ws["papers"].get(active_f) if active_f else None
        st.rerun()

    # Workspace Creator Expander
    with st.expander("➕ New Workspace"):
        new_ws_input = st.text_input("Workspace Name", placeholder="e.g. Climate Science")
        if st.button("Create Workspace", use_container_width=True):
            if new_ws_input and new_ws_input.strip():
                clean_ws = new_ws_input.strip()
                if clean_ws not in st.session_state["workspaces"]:
                    st.session_state["workspaces"][clean_ws] = {"papers": {}, "active": None}
                    st.session_state["active_workspace"] = clean_ws
                    st.success(f"Created '{clean_ws}'!")
                    st.rerun()
                else:
                    st.warning("Workspace already exists.")

    st.markdown("---")

    # --- 2. DOCUMENT LIST SECTION ---
    st.markdown("#### 📄 Papers in Workspace")
    current_papers = current_ws_data["papers"]
    if not current_papers:
        st.caption("No papers in this workspace yet. Upload a PDF or load the sample paper.")
    else:
        for fname, paper_proc in current_papers.items():
            is_active = (current_ws_data.get("active") == fname)
            active_badge = "🟢 " if is_active else "⚪ "
            col_doc1, col_doc2 = st.columns([4, 1])
            with col_doc1:
                st.markdown(f"**{active_badge}{paper_proc.title[:24]}...**" if len(paper_proc.title) > 24 else f"**{active_badge}{paper_proc.title}**")
                st.caption(f"{paper_proc.page_count} pages • {paper_proc.total_words:,} words")
            with col_doc2:
                if not is_active:
                    if st.button("Select", key=f"sel_{fname}", use_container_width=True):
                        set_active_document(fname)
                        st.rerun()

    st.markdown("---")

    # --- 3. MODEL CONFIGURATION SECTION ---
    st.markdown("#### ⚙️ Gemma 4 Model Setup")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_val = st.text_input(
        "Google AI Studio API Key",
        value=env_key if env_key else "",
        type="password",
        help="Session only. Kept strictly in memory. Never logged or exposed.",
        placeholder="AIzaSy...",
    )

    model_sel = st.selectbox(
        "Gemma Model Identifier",
        AVAILABLE_GEMMA_MODELS + ["Custom model..."],
        index=0 if DEFAULT_GEMMA_MODEL in AVAILABLE_GEMMA_MODELS else 0,
        help="Strictly targets Gemma 4 via Google Gen AI API.",
    )
    if model_sel == "Custom model...":
        active_model_id = st.text_input("Custom Model ID", value="gemma-4-26b-a4b-it")
    else:
        active_model_id = model_sel

    thinking_toggle = st.toggle(
        "Enable Thinking Mode",
        value=False,
        help="Enables thinking_level='high' on Gemma 4 for analytical research questions.",
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔌 Test Model", use_container_width=True):
            if not api_key_val:
                st.error("Enter API key.")
            else:
                with st.spinner("Pinging Gemma 4..."):
                    try:
                        client_probe = GemmaClient(api_key=api_key_val, model=active_model_id, enable_thinking=thinking_toggle)
                        succ, msg = client_probe.test_connection()
                        st.session_state["connection_status"] = (succ, msg)
                        st.session_state["last_tested_model"] = active_model_id
                        st.rerun()
                    except Exception as exc:
                        st.session_state["connection_status"] = (False, str(exc))
                        st.rerun()
    with col_btn2:
        if st.button("Reset State", use_container_width=True):
            st.session_state["summary"] = None
            st.session_state["chat_history"] = []
            st.session_state["insights"] = None
            st.session_state["figure_notes"] = []
            st.session_state["agent_reports"] = []
            st.session_state["last_synthesis"] = None
            st.session_state["last_citations"] = []
            st.success("Reset completed.")
            st.rerun()

    st.markdown("---")

    # --- 4. WORKSPACE STATISTICS ---
    st.markdown("#### 📊 Workspace Metrics")
    total_papers = len(current_papers)
    total_pages = sum(p.page_count for p in current_papers.values())
    total_words = sum(p.total_words for p in current_papers.values())
    total_chars = sum(p.total_chars for p in current_papers.values())

    st.markdown(
        f"""
        <div class="stat-box">
            <div class="stat-row"><span class="stat-label">Workspace Papers:</span><span class="stat-value">{total_papers}</span></div>
            <div class="stat-row"><span class="stat-label">Total Indexed Pages:</span><span class="stat-value">{total_pages}</span></div>
            <div class="stat-row"><span class="stat-label">Extracted Words:</span><span class="stat-value">{total_words:,}</span></div>
            <div class="stat-row"><span class="stat-label">Indexed Characters:</span><span class="stat-value">{total_chars:,}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🔒 Privacy & Grounding Notice"):
        st.caption(
            "• Zero remote PDF storage: parsing is 100% local via PyMuPDF.\n"
            "• Only extracted passages necessary for answering your query are transmitted to the API.\n"
            "• No silent model substitutions: requests strictly use Gemma 4."
        )


# Render top header bar
render_top_header(api_key=api_key_val, model_id=active_model_id)


# ---------------------------------------------------------------------------
# Helper: Get Initialized Gemma Client
# ---------------------------------------------------------------------------
def get_client() -> GemmaClient | None:
    if not api_key_val:
        return None
    try:
        return GemmaClient(
            api_key=api_key_val,
            model=active_model_id,
            enable_thinking=thinking_toggle,
        )
    except Exception as exc:
        st.error(f"Gemma 4 Client Error: {exc}")
        return None


# ---------------------------------------------------------------------------
# CENTRAL NAVIGATION BAR (Pill-shaped SaaS navigation)
# ---------------------------------------------------------------------------
nav_items = [
    ("📤 Upload", "Upload"),
    ("📚 Collection", "Collection"),
    ("🔍 Explorer", "Explorer"),
    ("💬 Chat", "Chat"),
    ("🧭 Insights", "Insights"),
    ("🖼️ Figures", "Figures"),
    ("🤖 Agent", "Agent"),
    ("📥 Export", "Export"),
]

nav_cols = st.columns(len(nav_items))
for idx, (label, view_key) in enumerate(nav_items):
    is_active = (st.session_state["active_nav"] == view_key)
    btn_type = "primary" if is_active else "secondary"
    if nav_cols[idx].button(label, key=f"nav_btn_{view_key}", use_container_width=True, type=btn_type):
        st.session_state["active_nav"] = view_key
        st.rerun()

current_view = st.session_state["active_nav"]
active_proc: PDFProcessor | None = st.session_state["pdf_processor"]


# ===========================================================================
# VIEW 1: UPLOAD (Polished Document Ingestion & Sample Loader)
# ===========================================================================
if current_view == "Upload":
    st.markdown("### 📤 Document Upload & Ingestion")
    st.markdown("Upload peer-reviewed research papers, preprints (arXiv/bioRxiv), or technical reports.")

    up_c1, up_c2 = st.columns([2, 1])

    with up_c1:
        st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload research paper (PDF)",
            type=["pdf"],
            help="Text-based PDFs are parsed locally. Scanned documents require OCR.",
        )

        if uploaded_file is not None:
            if uploaded_file.name not in workspace_papers:
                with st.spinner(f"Extracting and indexing '{uploaded_file.name}' locally with PyMuPDF..."):
                    try:
                        file_bytes = uploaded_file.getvalue()
                        new_proc = PDFProcessor(file_bytes=file_bytes, filename=uploaded_file.name)
                        is_valid, validation_err = new_proc.validate_content()
                        if not is_valid:
                            st.error(validation_err)
                        else:
                            workspace_papers[uploaded_file.name] = new_proc
                            set_active_document(uploaded_file.name)
                            st.success(f"Indexed '{uploaded_file.name}' into workspace '{current_ws_name}'!")
                            st.rerun()
                    except PDFProcessingError as pe:
                        st.error(f"PDF Error: {pe}")
                    except Exception as exc:
                        st.error(f"Unexpected error: {exc}")

        st.markdown("---")
        st.markdown("#### ⚡ Quick Start: Load Synthetic Sample Paper")
        st.caption("Test ResearchPilot AI immediately with a pre-indexed 3-page scientific research paper.")
        if st.button("📥 Load 'ResearchPilot: Autonomous Deep Scientific Literature Agents' (Sample PDF)", type="secondary"):
            sample_path = os.path.join("assets", "sample_paper_researchpilot.pdf")
            if os.path.exists(sample_path):
                with open(sample_path, "rb") as f:
                    s_bytes = f.read()
                s_proc = PDFProcessor(file_bytes=s_bytes, filename="sample_paper_researchpilot.pdf")
                workspace_papers["sample_paper_researchpilot.pdf"] = s_proc
                set_active_document("sample_paper_researchpilot.pdf")
                st.success("Loaded sample research paper! Switch to 'Explorer' or 'Chat' to test.")
                st.rerun()
            else:
                st.error("Sample paper asset not found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with up_c2:
        st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
        st.markdown("#### 📑 Active Document Status")
        if active_proc:
            p_stats = active_proc.get_summary_statistics()
            st.markdown(f"**Title:** {p_stats['title']}")
            st.caption(f"File: `{p_stats['filename']}`")
            st.metric("Total Pages", p_stats["page_count"])
            st.metric("Extracted Words", f"{p_stats['total_words']:,}")
            st.metric("Reading Time", f"{p_stats['estimated_reading_minutes']} min")
            if p_stats["sections_detected"]:
                st.markdown(f"**Detected Sections:** `{', '.join(p_stats['sections_detected'][:5])}`")
        else:
            st.info("No active document selected. Upload a PDF or click the Quick Start button.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Document text preview if loaded
    if active_proc:
        with st.expander("📖 Preview Extracted Document Text (Page-by-Page)"):
            preview_page = st.slider("Select Preview Page", 1, active_proc.page_count, 1)
            st.code(active_proc.get_page_text(preview_page)[:3000], language="text")


# ===========================================================================
# VIEW 2: COLLECTION (Workspace Library Grid)
# ===========================================================================
elif current_view == "Collection":
    st.markdown(f"### 📚 Paper Collection: *{current_ws_name}*")
    st.markdown("Manage and switch between active research papers within this workspace.")

    if not workspace_papers:
        st.info("This workspace is currently empty. Switch to the 'Upload' tab to add research papers.")
    else:
        for fname, paper_proc in list(workspace_papers.items()):
            is_active = (current_ws_data.get("active") == fname)
            active_style = "border-color: #3b82f6; background: #13203b;" if is_active else ""

            st.markdown(
                f"""
                <div class="workspace-panel" style="{active_style}">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <span style="font-size:0.75rem; color:{'#38bdf8' if is_active else '#94a3b8'}; font-weight:700;">
                                {'● ACTIVE DOCUMENT' if is_active else '○ INACTIVE'}
                            </span>
                            <h3 style="margin:0.2rem 0 0.4rem 0; color:#ffffff; font-size:1.15rem;">{paper_proc.title}</h3>
                            <span style="color:#94a3b8; font-size:0.8rem;">Filename: <code>{fname}</code></span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_c1, c_c2, c_c3, c_c4 = st.columns([2, 2, 2, 2])
            c_c1.metric("Pages", paper_proc.page_count)
            c_c2.metric("Words", f"{paper_proc.total_words:,}")
            c_c3.metric("Reading Time", f"{round(paper_proc.total_words/200, 1)} min")
            with c_c4:
                if not is_active:
                    if st.button("Set as Active", key=f"set_act_{fname}", use_container_width=True):
                        set_active_document(fname)
                        st.rerun()
                else:
                    st.button("Active Document", disabled=True, key=f"is_act_{fname}", use_container_width=True)


# ===========================================================================
# VIEW 3: EXPLORER (The Flagship 3-Area Research RAG Workspace)
# ===========================================================================
elif current_view == "Explorer":
    # 2-Column Responsive Layout: Central Workspace (70%) + Right Context Panel (30%)
    col_center, col_right = st.columns([7, 3])

    # -----------------------------------------------------------------------
    # LEFT / CENTRAL WORKSPACE: Query Panel & AI Synthesis
    # -----------------------------------------------------------------------
    with col_center:
        # --- CENTRAL QUERY PANEL ---
        st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel-header-row">
                <div class="panel-title">⚡ Research Query Panel</div>
                <div class="panel-subtitle">Grounded in paper text with [PAGE N] citations</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        inquiry_text = st.text_area(
            "Research Question",
            value=st.session_state.get("last_query", ""),
            placeholder="Ask about methodology, experimental results, model architecture, limitations, or compare your research papers...",
            height=85,
            label_visibility="collapsed",
        )

        # Quick Suggestion Chips
        chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
        chip_q = None
        if chip_col1.button("⚙️ Methodology", use_container_width=True):
            chip_q = "Explain the proposed methodology, architecture, and algorithms in plain terms."
        if chip_col2.button("📊 Results & Baselines", use_container_width=True):
            chip_q = "What exact quantitative results, metrics, and baselines did the authors report?"
        if chip_col3.button("📂 Datasets Used", use_container_width=True):
            chip_q = "What datasets, data sources, splits, and preprocessing steps were utilized?"
        if chip_col4.button("⚠️ Stated Limitations", use_container_width=True):
            chip_q = "What specific limitations, assumptions, and constraints did the authors state?"

        query_to_run = chip_q or inquiry_text

        col_ask, col_sum = st.columns([2, 1])
        with col_ask:
            ask_gemma_btn = st.button("⚡ Ask Gemma 4", type="primary", use_container_width=True)
        with col_sum:
            generate_summary_btn = st.button("📑 Generate Full Summary", type="secondary", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Execute Query / Synthesis
        if ask_gemma_btn and query_to_run.strip():
            if not active_proc:
                st.error("Please upload or select an active research paper first (Upload tab).")
            else:
                client = get_client()
                if not client:
                    st.error("Please configure your Google AI Studio API key in the sidebar.")
                else:
                    with st.spinner("Gemma 4 is retrieving evidence and synthesizing grounded findings..."):
                        start_t = time.time()
                        try:
                            # 1. Search relevant pages for grounding
                            matches = active_proc.search_pages(query_to_run, top_k=4)
                            citations = []
                            for idx, m in enumerate(matches, 1):
                                citations.append({
                                    "id": f"SR-{idx}",
                                    "title": active_proc.title,
                                    "page_number": m["page_number"],
                                    "snippet": m["snippet"],
                                    "score": m["score"],
                                })
                            st.session_state["last_citations"] = citations

                            # 2. Build grounded context budget
                            grounded_ctx = active_proc.get_grounded_context_for_query(query_to_run)
                            qa_prompt = prompts.build_qa_prompt(
                                paper_context=grounded_ctx,
                                user_question=query_to_run,
                                chat_history=st.session_state["chat_history"],
                            )
                            answer = client.generate_text(
                                prompt=qa_prompt,
                                system_instruction=prompts.SYSTEM_INSTRUCTION,
                                thinking=thinking_toggle,
                            )
                            duration = round(time.time() - start_t, 2)

                            st.session_state["last_query"] = query_to_run
                            st.session_state["last_synthesis"] = answer
                            st.session_state["last_query_duration"] = duration

                            # Also save into chat history
                            st.session_state["chat_history"].append({"role": "user", "content": query_to_run})
                            st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                        except GemmaClientError as ge:
                            st.error(f"Gemma Request Failed: {ge}")
                        except Exception as exc:
                            st.error(f"Error: {exc}")

        elif generate_summary_btn:
            if not active_proc:
                st.error("Please upload or select an active research paper first.")
            else:
                client = get_client()
                if not client:
                    st.error("Please configure your Google AI Studio API key in the sidebar.")
                else:
                    with st.spinner("Gemma 4 is reading and compiling the structured research summary..."):
                        start_t = time.time()
                        try:
                            context = active_proc.get_full_text(max_chars=PDFProcessor.DEFAULT_MAX_CONTEXT_CHARS)
                            s_prompt = prompts.build_summary_prompt(context, title=active_proc.title)
                            summary_resp = client.generate_text(
                                prompt=s_prompt,
                                system_instruction=prompts.SYSTEM_INSTRUCTION,
                                thinking=thinking_toggle,
                            )
                            duration = round(time.time() - start_t, 2)
                            st.session_state["summary"] = summary_resp
                            st.session_state["last_query"] = "Full 12-Point Structured Research Summary"
                            st.session_state["last_synthesis"] = summary_resp
                            st.session_state["last_query_duration"] = duration

                            # Set citations from main sections
                            matches = active_proc.search_pages("Methodology Experiments Results Conclusion", top_k=3)
                            st.session_state["last_citations"] = [
                                {
                                    "id": f"SR-{idx}",
                                    "title": active_proc.title,
                                    "page_number": m["page_number"],
                                    "snippet": m["snippet"],
                                    "score": m["score"],
                                }
                                for idx, m in enumerate(matches, 1)
                            ]
                        except GemmaClientError as ge:
                            st.error(f"Gemma Summary Error: {ge}")
                        except Exception as exc:
                            st.error(f"Error: {exc}")

        # --- MAIN RESULTS PANEL ("AI SYNTHESIS") ---
        st.markdown('<div class="synthesis-card">', unsafe_allow_html=True)

        synth_content = st.session_state.get("last_synthesis")
        dur = st.session_state.get("last_query_duration")
        citations_count = len(st.session_state.get("last_citations", []))

        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                <div style="display:flex; align-items:center; gap:0.5rem;">
                    <span style="font-size:1.1rem; color:#38bdf8;">⚡</span>
                    <strong style="font-size:1rem; letter-spacing:0.04em; color:#ffffff;">RESEARCH SYNTHESIS</strong>
                </div>
                <div style="display:flex; gap:0.5rem;">
                    <span class="meta-chip meta-chip-blue">Model: {active_model_id}</span>
                    {f'<span class="meta-chip">⏱️ {dur}s</span>' if dur else ''}
                    <span class="meta-chip">📑 {citations_count} Supporting Passages</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if synth_content:
            st.markdown(synth_content)
            st.markdown("---")
            act_c1, act_c2, act_c3 = st.columns([1, 1, 2])
            with act_c1:
                md_down, md_fname = export_summary_markdown(
                    active_proc.title if active_proc else "Research_Synthesis",
                    synth_content,
                    active_proc.get_summary_statistics() if active_proc else None,
                )
                st.download_button("📥 Download (.md)", md_down, md_fname, mime="text/markdown", use_container_width=True)
            with act_c2:
                if st.button("💬 Discuss in Chat", use_container_width=True):
                    st.session_state["active_nav"] = "Chat"
                    st.rerun()
        else:
            st.info(
                "💡 **Ready for Analysis**\n\n"
                "Enter a research inquiry above or click one of the preset chips (Methodology, Results, Datasets, Limitations), "
                "then click **Ask Gemma 4** to generate a grounded synthesis."
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # RIGHT CONTEXT PANEL: Document Scope & Source Citations
    # -----------------------------------------------------------------------
    with col_right:
        # --- 1. PAPER SCOPE ---
        st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="panel-header-row">
                <div class="panel-title">📄 Paper Scope</div>
                <span class="meta-chip meta-chip-blue">{'1 Active' if active_proc else '0 Active'}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if active_proc:
            p_stats = active_proc.get_summary_statistics()
            st.markdown(
                f"""
                <div class="doc-card active">
                    <div class="doc-card-title">{p_stats['title']}</div>
                    <div class="doc-card-meta">
                        Pages: <strong>{p_stats['page_count']}</strong> •
                        Words: <strong>{p_stats['total_words']:,}</strong> •
                        Read: <strong>{p_stats['estimated_reading_minutes']}m</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if len(workspace_papers) > 1:
                st.caption(f"+ {len(workspace_papers) - 1} other paper(s) in this workspace. Switch in sidebar or Collection tab.")
        else:
            st.caption("No document currently loaded. Upload a PDF or click Quick Start.")
        st.markdown("</div>", unsafe_allow_html=True)

        # --- 2. SOURCE CITATIONS ---
        st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
        current_citations = st.session_state.get("last_citations", [])
        st.markdown(
            f"""
            <div class="panel-header-row">
                <div class="panel-title">📌 Source Citations</div>
                <span class="meta-chip">{len(current_citations)} Verified</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if current_citations:
            for cit in current_citations:
                st.markdown(
                    f"""
                    <div class="citation-card">
                        <div class="citation-header">
                            <span class="citation-id">{cit['id']}</span>
                            <span class="citation-loc">Page {cit['page_number']}</span>
                        </div>
                        <div class="citation-body">"{cit['snippet']}"</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<p style="font-size:0.82rem; color:#94a3b8; font-style:italic;">No supporting passages available for this response.</p>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# VIEW 4: CHAT (Interactive Grounded Multi-Turn Dialogue)
# ===========================================================================
elif current_view == "Chat":
    st.markdown("### 💬 Interactive Research Dialogue")
    st.markdown("Engage in a continuous multi-turn dialogue with Gemma 4, grounded in the active paper.")

    if not active_proc:
        st.warning("Please upload a paper in the 'Upload' tab to chat with it.")
    else:
        # Display Message History
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input box
        chat_q = st.chat_input("Ask a follow-up question or probe deeper into the methodology...")
        if chat_q:
            st.session_state["chat_history"].append({"role": "user", "content": chat_q})
            with st.chat_message("user"):
                st.markdown(chat_q)

            client = get_client()
            if not client:
                st.error("Please configure your Google AI Studio API key in the sidebar.")
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Gemma 4 is retrieving context..."):
                        try:
                            # Ground context
                            grounded_context = active_proc.get_grounded_context_for_query(chat_q)
                            prompt = prompts.build_qa_prompt(
                                paper_context=grounded_context,
                                user_question=chat_q,
                                chat_history=st.session_state["chat_history"][:-1],
                            )
                            ans = client.generate_text(
                                prompt=prompt,
                                system_instruction=prompts.SYSTEM_INSTRUCTION,
                                thinking=thinking_toggle,
                            )
                            st.markdown(ans)
                            st.session_state["chat_history"].append({"role": "assistant", "content": ans})

                            # Update last synthesis and citations
                            st.session_state["last_synthesis"] = ans
                            matches = active_proc.search_pages(chat_q, top_k=3)
                            st.session_state["last_citations"] = [
                                {
                                    "id": f"SR-{idx}",
                                    "title": active_proc.title,
                                    "page_number": m["page_number"],
                                    "snippet": m["snippet"],
                                    "score": m["score"],
                                }
                                for idx, m in enumerate(matches, 1)
                            ]
                        except GemmaClientError as ge:
                            st.error(f"Gemma Error: {ge}")
                        except Exception as exc:
                            st.error(f"Failed: {exc}")

        # Chat actions
        if st.session_state["chat_history"]:
            st.markdown("---")
            c_cl, c_exp = st.columns([1, 2])
            with c_cl:
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    st.session_state["chat_history"] = []
                    st.rerun()
            with c_exp:
                c_md, c_fname = export_chat_markdown(
                    active_proc.title,
                    st.session_state["chat_history"],
                    active_proc.get_summary_statistics(),
                )
                st.download_button("📥 Export Dialogue Transcript (.md)", c_md, c_fname, mime="text/markdown", use_container_width=True)


# ===========================================================================
# VIEW 5: INSIGHTS (Limitations & Future Directions)
# ===========================================================================
elif current_view == "Insights":
    st.markdown("### 🧭 Research Insights, Limitations & Opportunities")
    st.markdown(
        "Examine the paper's critical boundary conditions. Gemma 4 separates explicitly stated author limitations "
        "from inferred constraints and produces 3 to 5 actionable research proposals with suggested experiments."
    )

    if not active_proc:
        st.warning("Please upload a paper in the 'Upload' tab to analyze research insights.")
    else:
        if st.button("Analyze Research Opportunities", type="primary"):
            client = get_client()
            if not client:
                st.error("Please configure your Google AI Studio API key in the sidebar.")
            else:
                with st.spinner("Gemma 4 is evaluating methodology, assumptions, and research gaps..."):
                    try:
                        ctx = active_proc.get_full_text(max_chars=PDFProcessor.DEFAULT_MAX_CONTEXT_CHARS)
                        i_prompt = prompts.build_insights_prompt(ctx)
                        insights_resp = client.generate_text(
                            prompt=i_prompt,
                            system_instruction=prompts.SYSTEM_INSTRUCTION,
                            thinking=thinking_toggle,
                        )
                        st.session_state["insights"] = insights_resp
                        st.success("Research Insights and Opportunities Report generated!")
                    except GemmaClientError as ge:
                        st.error(f"Gemma Request Failed: {ge}")
                    except Exception as exc:
                        st.error(f"Error: {exc}")

        if st.session_state.get("insights"):
            st.markdown('<div class="synthesis-card">', unsafe_allow_html=True)
            st.markdown(st.session_state["insights"])
            st.markdown("</div>", unsafe_allow_html=True)

            ins_md, ins_fn = export_insights_markdown(
                active_proc.title,
                st.session_state["insights"],
                active_proc.get_summary_statistics(),
            )
            st.download_button("📥 Download Research Insights Report (.md)", ins_md, ins_fn, mime="text/markdown")


# ===========================================================================
# VIEW 6: FIGURES (Multimodal Visual Analysis)
# ===========================================================================
elif current_view == "Figures":
    st.markdown("### 🖼️ Multimodal Figure, Chart & Diagram Analysis")
    st.markdown("Render any PDF page in high resolution and let Gemma 4 visually inspect architecture diagrams, loss curves, and tables.")

    if not active_proc:
        st.warning("Please upload a paper in the 'Upload' tab to analyze figures.")
    else:
        v_col1, v_col2 = st.columns([1, 1])

        with v_col1:
            st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
            st.markdown("#### ⚙️ Page Selection & Inspection Query")
            v_page = st.number_input("Select Page Number", 1, active_proc.page_count, 1)
            v_zoom = st.select_slider("Zoom (Resolution)", [1.0, 1.5, 2.0], value=1.5, format_func=lambda x: f"{x}x")

            v_presets = [
                "Explain the visible architecture or system flow diagram in detail.",
                "What trends, axes, baselines, and inflection points are shown in the charts?",
                "Summarize the experimental comparison or table visible on this page.",
                "Explain this diagram in simple terms for a beginner.",
            ]
            v_choice = st.selectbox("Preset Visual Questions", v_presets)
            v_custom_q = st.text_input("Or custom question:", value=v_choice)

            run_vision_btn = st.button("🔍 Analyze Page with Gemma 4", type="primary", use_container_width=True)

            # Render page image
            try:
                rendered_png = active_proc.render_page_image(int(v_page), zoom=float(v_zoom))
                st.image(rendered_png, caption=f"PDF Page {v_page} (Rendered at {v_zoom}x)", use_container_width=True)
            except Exception as exc:
                st.error(f"Render failed: {exc}")
                rendered_png = None
            st.markdown("</div>", unsafe_allow_html=True)

        with v_col2:
            st.markdown('<div class="synthesis-card">', unsafe_allow_html=True)
            st.markdown("#### 🔬 Visual Inspection Findings")

            if run_vision_btn and rendered_png:
                client = get_client()
                if not client:
                    st.error("Configure Google AI Studio API key in sidebar.")
                else:
                    with st.spinner(f"Gemma 4 is visually inspecting Page {v_page}..."):
                        try:
                            p_text = active_proc.get_page_text(int(v_page))
                            vf_prompt = prompts.build_figure_analysis_prompt(
                                user_question=v_custom_q,
                                page_number=int(v_page),
                                page_text=p_text,
                            )
                            vf_res = client.generate_with_image(
                                prompt=vf_prompt,
                                image_bytes=rendered_png,
                                mime_type="image/png",
                                system_instruction=prompts.SYSTEM_INSTRUCTION,
                                thinking=thinking_toggle,
                            )
                            st.markdown(vf_res)
                            st.session_state["figure_notes"].append({
                                "page": int(v_page),
                                "question": v_custom_q,
                                "analysis": vf_res,
                            })

                            fig_md, fig_fn = export_figure_analysis_markdown(
                                active_proc.title,
                                int(v_page),
                                v_custom_q,
                                vf_res,
                                active_proc.get_summary_statistics(),
                            )
                            st.download_button("📥 Download Visual Notes (.md)", fig_md, fig_fn, mime="text/markdown")
                        except GemmaClientError as ge:
                            st.error(f"Visual Analysis Error: {ge}")
                        except Exception as exc:
                            st.error(f"Error: {exc}")
            else:
                st.caption("Select a page and click 'Analyze Page with Gemma 4' to generate visual insights.")
            st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# VIEW 7: AGENT (Autonomous Research Investigation & Tool Trace)
# ===========================================================================
elif current_view == "Agent":
    st.markdown("### 🤖 Autonomous Research Agent")
    st.markdown(
        "Run an autonomous research agent that formulates an evidence-gathering plan, "
        "invokes registered document tools, and synthesizes a verifiable research finding with full execution traces."
    )

    if not active_proc:
        st.warning("Please upload a paper in the 'Upload' tab to launch an agent investigation.")
    else:
        ag_c1, ag_c2 = st.columns([2, 1])
        with ag_c1:
            st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
            ag_target = st.text_input(
                "Agent Investigation Target",
                value="Examine the dataset size, preprocessing steps, and data splits used in the experiments.",
            )
            launch_ag_btn = st.button("🚀 Launch Agent Investigation", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with ag_c2:
            st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
            st.markdown("#### 🛡️ Registered Safe Tools")
            st.code("• get_paper_metadata\n• get_page_text\n• search_paper_text\n• get_paper_statistics\n• render_pdf_page", language="text")
            st.caption("No arbitrary shell or code execution. Strictly read-only sandboxed tools.")
            st.markdown("</div>", unsafe_allow_html=True)

        if launch_ag_btn and ag_target.strip():
            client = get_client()
            agent = ResearchAgent(pdf_processor=active_proc, gemma_client=client)

            with st.spinner("Agent is running tool execution loop..."):
                ag_result = agent.run_agentic_investigation(user_query=ag_target, max_steps=5)
                st.session_state["agent_reports"].append(ag_result)
                st.success(f"Investigation completed! Executed {ag_result['tool_calls_count']} tool steps.")

                st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
                st.markdown("#### 🔍 Tool Execution Trace")
                for step in ag_result["execution_trace"]:
                    st.markdown(
                        f"""
                        <div style="background:#0d1527; border-left:3px solid #38bdf8; padding:0.55rem 0.85rem; margin-bottom:0.45rem; border-radius:0 6px 6px 0;">
                            <strong>Step {step['step']}: <code>{step['tool']}</code></strong> ({step['status']})<br>
                            <span style="color:#94a3b8; font-size:0.82rem;">{step['summary']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown('<div class="synthesis-card">', unsafe_allow_html=True)
                st.markdown("#### 📑 Synthesized Agent Findings")
                st.markdown(ag_result["synthesized_answer"])
                st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# VIEW 8: EXPORT (Dossier & Artifacts Center)
# ===========================================================================
elif current_view == "Export":
    st.markdown("### 📥 Research Dossier & Export Center")
    st.markdown("Download individual research notes or export the complete, consolidated Research Dossier.")

    if not active_proc:
        st.warning("Please upload a paper in the 'Upload' tab to export research results.")
    else:
        p_stats = active_proc.get_summary_statistics()
        exp_col1, exp_col2 = st.columns([1, 1])

        with exp_col1:
            st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
            st.markdown("#### 📄 Individual Artifacts")

            if st.session_state.get("summary"):
                s_md, s_file = export_summary_markdown(active_proc.title, st.session_state["summary"], p_stats)
                st.download_button("📥 Download Summary (.md)", s_md, s_file, mime="text/markdown", use_container_width=True)
            else:
                st.caption("• Paper Summary not generated yet.")

            if st.session_state.get("chat_history"):
                c_md, c_file = export_chat_markdown(active_proc.title, st.session_state["chat_history"], p_stats)
                st.download_button("📥 Download Q&A Dialogue (.md)", c_md, c_file, mime="text/markdown", use_container_width=True)
            else:
                st.caption("• No active Q&A history recorded.")

            if st.session_state.get("insights"):
                i_md, i_file = export_insights_markdown(active_proc.title, st.session_state["insights"], p_stats)
                st.download_button("📥 Download Research Insights (.md)", i_md, i_file, mime="text/markdown", use_container_width=True)
            else:
                st.caption("• Research insights report not generated yet.")
            st.markdown("</div>", unsafe_allow_html=True)

        with exp_col2:
            st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
            st.markdown("#### 📦 Unified Complete Research Dossier")
            st.markdown("Consolidates all summaries, dialogue transcripts, insights, figure notes, and agent traces into a single Markdown document.")

            dossier_md, dossier_filename = export_complete_dossier_markdown(
                title=active_proc.title,
                metadata=p_stats,
                summary=st.session_state.get("summary"),
                chat_history=st.session_state.get("chat_history"),
                insights=st.session_state.get("insights"),
                figure_notes=st.session_state.get("figure_notes"),
                agent_reports=st.session_state.get("agent_reports"),
            )

            st.download_button(
                "📦 Download Complete Research Dossier (.md)",
                data=dossier_md,
                file_name=dossier_filename,
                mime="text/markdown",
                type="primary",
                use_container_width=True,
            )

            with st.expander("Preview Dossier"):
                st.code(dossier_md[:1200] + "\n\n...[Full content in export file]...", language="markdown")
            st.markdown("</div>", unsafe_allow_html=True)
