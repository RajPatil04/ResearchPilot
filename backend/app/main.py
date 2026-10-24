"""FastAPI HTTP backend for ResearchPilot AI React frontend."""

from __future__ import annotations

import asyncio
import io
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

import src.prompts as prompts
from src.export_utils import (
    export_chat_markdown,
    export_complete_dossier_markdown,
    export_figure_analysis_markdown,
    export_insights_markdown,
    export_summary_markdown,
)
from src.gemma_client import AVAILABLE_GEMMA_MODELS, GemmaClientError
from src.pdf_processor import PDFProcessingError
from src.research_agent import ResearchAgent

from .schemas import (
    AgentInvestigationRequest,
    AgentInvestigationResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    Citation,
    ConnectRequest,
    ConnectResponse,
    ConversationSession,
    DocumentMetadata,
    ExportRequest,
    FigureAnalysisRequest,
    FigureAnalysisResponse,
    InsightsResponse,
    ModelInfo,
    SummaryResponse,
)
from .state import backend_state

app = FastAPI(
    title="ResearchPilot AI Backend",
    description="FastAPI service powering ResearchPilot AI React frontend with Gemma 4",
    version="2.0.0",
)
app.max_body_size = None

# Enable CORS for local Vite dev server and production ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper: Convert PDFProcessor to DocumentMetadata
# ---------------------------------------------------------------------------
def _to_doc_metadata(doc_id: str, proc, is_active: bool = False) -> DocumentMetadata:
    stats = proc.get_summary_statistics()
    return DocumentMetadata(
        id=doc_id,
        title=stats["title"],
        filename=stats["filename"],
        page_count=stats["page_count"],
        total_words=stats["total_words"],
        total_characters=stats["total_characters"],
        estimated_reading_minutes=stats["estimated_reading_minutes"],
        sections_detected=stats["sections_detected"],
        is_scanned=stats["is_scanned"],
        is_active=is_active,
    )


# ---------------------------------------------------------------------------
# Core System Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
def get_health() -> Dict[str, Any]:
    conn_ok = False
    if backend_state.connection_status:
        conn_ok = backend_state.connection_status[0]
    return {
        "status": "healthy",
        "model": backend_state.model,
        "has_api_key": bool(backend_state.api_key),
        "connected": conn_ok,
        "documents_count": len(backend_state.documents),
        "active_document_id": backend_state.active_document_id,
    }


@app.get("/api/models")
def get_models() -> Dict[str, Any]:
    models = [
        ModelInfo(
            id="gemma-4-26b-a4b-it",
            name="Gemma 4 26B (Default)",
            is_default=True,
            description="Recommended default model for literature synthesis and grounded scientific reasoning.",
        ),
        ModelInfo(
            id="gemma-4-31b-it",
            name="Gemma 4 31B",
            is_default=False,
            description="High-capacity Gemma 4 model for deep comparative analysis.",
        ),
    ]
    return {
        "models": [m.model_dump() for m in models],
        "active_model": backend_state.model,
        "enable_thinking": backend_state.enable_thinking,
    }


@app.post("/api/connect", response_model=ConnectResponse)
def connect_model(req: ConnectRequest) -> ConnectResponse:
    if not req.api_key or not req.api_key.strip():
        raise HTTPException(status_code=400, detail="API key cannot be empty.")

    backend_state.api_key = req.api_key.strip()
    if req.model:
        backend_state.model = req.model.strip()
    if req.enable_thinking is not None:
        backend_state.enable_thinking = req.enable_thinking

    success, msg = backend_state.verify_connection()
    return ConnectResponse(
        success=success,
        message=msg,
        model=backend_state.model,
        has_api_key=True,
    )


# ---------------------------------------------------------------------------
# Document Management Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/documents/upload", response_model=DocumentMetadata)
async def upload_document(file: UploadFile = File(...)) -> DocumentMetadata:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

    try:
        doc_id, proc = backend_state.add_document(content, file.filename)
        is_valid, validation_err = proc.validate_content()
        if not is_valid:
            backend_state.remove_document(doc_id)
            raise HTTPException(status_code=400, detail=validation_err)

        return _to_doc_metadata(doc_id, proc, is_active=True)
    except PDFProcessingError as pe:
        raise HTTPException(status_code=400, detail=str(pe))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {exc}")


@app.post("/api/documents/sample", response_model=DocumentMetadata)
def load_sample_document() -> DocumentMetadata:
    res = backend_state.load_sample_paper()
    if not res:
        raise HTTPException(status_code=404, detail="Sample research paper asset not found.")
    doc_id, proc = res
    return _to_doc_metadata(doc_id, proc, is_active=True)


@app.get("/api/documents", response_model=List[DocumentMetadata])
def list_documents() -> List[DocumentMetadata]:
    res = []
    for doc_id, proc in backend_state.documents.items():
        is_active = (doc_id == backend_state.active_document_id)
        res.append(_to_doc_metadata(doc_id, proc, is_active=is_active))
    return res


@app.get("/api/documents/{document_id}", response_model=DocumentMetadata)
def get_document(document_id: str) -> DocumentMetadata:
    proc = backend_state.get_document_by_id(document_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Document not found.")
    is_active = (document_id == backend_state.active_document_id)
    return _to_doc_metadata(document_id, proc, is_active=is_active)


@app.post("/api/documents/{document_id}/select")
def select_document(document_id: str) -> Dict[str, Any]:
    if document_id not in backend_state.documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    backend_state.active_document_id = document_id
    return {"success": True, "active_document_id": document_id}


@app.delete("/api/documents/{document_id}")
def delete_document(document_id: str) -> Dict[str, Any]:
    removed = backend_state.remove_document(document_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"success": True, "removed_id": document_id}


# ---------------------------------------------------------------------------
# Research Chat & Streaming Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
def chat_message(req: ChatRequest) -> ChatResponse:
    doc = None
    if req.document_id:
        doc = backend_state.get_document_by_id(req.document_id)
    if not doc:
        doc = backend_state.get_active_document()

    client = backend_state.get_client()
    if not client:
        raise HTTPException(
            status_code=400,
            detail="Gemma 4 client not configured. Please enter your Google AI Studio API key in Settings.",
        )

    start_time = time.time()
    citations: List[Citation] = []
    grounded_context = ""

    if doc:
        # Retrieve lexical matches for citations
        matches = doc.search_pages(req.message, top_k=4)
        for idx, m in enumerate(matches, 1):
            citations.append(Citation(
                id=f"SR-{idx}",
                title=doc.title,
                page_number=m["page_number"],
                snippet=m["snippet"],
                score=m["score"],
            ))
        grounded_context = doc.get_grounded_context_for_query(req.message)

    history_dicts = [{"role": m.role, "content": m.content} for m in (req.history or [])]
    prompt = prompts.build_qa_prompt(
        paper_context=grounded_context if grounded_context else "No document selected.",
        user_question=req.message,
        chat_history=history_dicts,
    )

    try:
        response_text = client.generate_text(
            prompt=prompt,
            system_instruction=prompts.SYSTEM_INSTRUCTION,
            thinking=backend_state.enable_thinking,
        )
        duration = round(time.time() - start_time, 2)
        return ChatResponse(
            response=response_text,
            citations=citations,
            model=backend_state.model,
            duration_seconds=duration,
            document_id=req.document_id or backend_state.active_document_id,
        )
    except GemmaClientError as ge:
        raise HTTPException(status_code=502, detail=str(ge))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference error: {exc}")


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    """Server-Sent Events (SSE) streaming endpoint for ChatGPT-style response generation."""
    doc = None
    if req.document_id:
        doc = backend_state.get_document_by_id(req.document_id)
    if not doc:
        doc = backend_state.get_active_document()

    client = backend_state.get_client()
    if not client:
        raise HTTPException(status_code=400, detail="API key not configured in Settings.")

    citations: List[Citation] = []
    grounded_context = ""
    if doc:
        matches = doc.search_pages(req.message, top_k=4)
        for idx, m in enumerate(matches, 1):
            citations.append(Citation(
                id=f"SR-{idx}",
                title=doc.title,
                page_number=m["page_number"],
                snippet=m["snippet"],
                score=m["score"],
            ))
        grounded_context = doc.get_grounded_context_for_query(req.message)

    history_dicts = [{"role": m.role, "content": m.content} for m in (req.history or [])]
    prompt = prompts.build_qa_prompt(
        paper_context=grounded_context if grounded_context else "No document attached.",
        user_question=req.message,
        chat_history=history_dicts,
    )

    def event_generator():
        import json
        try:
            full_text = client.generate_text(
                prompt=prompt,
                system_instruction=prompts.SYSTEM_INSTRUCTION,
                thinking=backend_state.enable_thinking,
            )
            # Yield tokens smoothly to emulate streaming chunks
            chunk_size = 28
            for i in range(0, len(full_text), chunk_size):
                token = full_text[i:i + chunk_size]
                payload = json.dumps({"token": token})
                yield f"data: {payload}\n\n"
                time.sleep(0.02)

            # Final metadata event with citations
            citations_data = [c.model_dump() for c in citations]
            meta_payload = json.dumps({"done": True, "citations": citations_data})
            yield f"data: {meta_payload}\n\n"
        except Exception as exc:
            err_payload = json.dumps({"error": str(exc)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Research Tools: Summary & Insights Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/documents/{document_id}/summary", response_model=SummaryResponse)
def generate_summary(document_id: str) -> SummaryResponse:
    doc = backend_state.get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    client = backend_state.get_client()
    if not client:
        raise HTTPException(status_code=400, detail="API key not configured in Settings.")

    start_time = time.time()
    try:
        context = doc.get_full_text(max_chars=55000)
        s_prompt = prompts.build_summary_prompt(context, title=doc.title)
        summary_text = client.generate_text(
            prompt=s_prompt,
            system_instruction=prompts.SYSTEM_INSTRUCTION,
            thinking=backend_state.enable_thinking,
        )
        duration = round(time.time() - start_time, 2)

        matches = doc.search_pages("Methodology Results Conclusion Limitations", top_k=3)
        citations = [
            Citation(id=f"SR-{i}", title=doc.title, page_number=m["page_number"], snippet=m["snippet"], score=m["score"])
            for i, m in enumerate(matches, 1)
        ]

        return SummaryResponse(
            summary=summary_text,
            metadata=_to_doc_metadata(document_id, doc, is_active=True),
            citations=citations,
            duration_seconds=duration,
        )
    except GemmaClientError as ge:
        raise HTTPException(status_code=502, detail=str(ge))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summary generation error: {exc}")


@app.post("/api/documents/{document_id}/insights", response_model=InsightsResponse)
def generate_insights(document_id: str) -> InsightsResponse:
    doc = backend_state.get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    client = backend_state.get_client()
    if not client:
        raise HTTPException(status_code=400, detail="API key not configured in Settings.")

    start_time = time.time()
    try:
        context = doc.get_full_text(max_chars=55000)
        i_prompt = prompts.build_insights_prompt(context)
        insights_text = client.generate_text(
            prompt=i_prompt,
            system_instruction=prompts.SYSTEM_INSTRUCTION,
            thinking=backend_state.enable_thinking,
        )
        duration = round(time.time() - start_time, 2)
        return InsightsResponse(
            insights=insights_text,
            metadata=_to_doc_metadata(document_id, doc, is_active=True),
            duration_seconds=duration,
        )
    except GemmaClientError as ge:
        raise HTTPException(status_code=502, detail=str(ge))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Insights error: {exc}")


# ---------------------------------------------------------------------------
# Multimodal Figures Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/documents/{document_id}/pages/{page_no}/image")
def get_page_image(document_id: str, page_no: int, zoom: float = 1.5):
    doc = backend_state.get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        png_bytes = doc.render_page_image(page_no, zoom=zoom)
        return Response(content=png_bytes, media_type="image/png")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/documents/{document_id}/figures/analyze", response_model=FigureAnalysisResponse)
def analyze_figure(document_id: str, req: FigureAnalysisRequest) -> FigureAnalysisResponse:
    doc = backend_state.get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    client = backend_state.get_client()
    if not client:
        raise HTTPException(status_code=400, detail="API key not configured in Settings.")

    try:
        png_bytes = doc.render_page_image(req.page_number, zoom=req.zoom or 1.5)
        page_text = doc.get_page_text(req.page_number)
        fig_prompt = prompts.build_figure_analysis_prompt(
            user_question=req.question,
            page_number=req.page_number,
            page_text=page_text,
        )
        analysis_text = client.generate_with_image(
            prompt=fig_prompt,
            image_bytes=png_bytes,
            mime_type="image/png",
            system_instruction=prompts.SYSTEM_INSTRUCTION,
            thinking=backend_state.enable_thinking,
        )
        return FigureAnalysisResponse(
            analysis=analysis_text,
            page_number=req.page_number,
            question=req.question,
            document_id=document_id,
        )
    except GemmaClientError as ge:
        raise HTTPException(status_code=502, detail=str(ge))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Figure analysis error: {exc}")


# ---------------------------------------------------------------------------
# Agentic Investigation Endpoint
# ---------------------------------------------------------------------------
@app.post("/api/agent/investigate", response_model=AgentInvestigationResponse)
def run_agent_investigation(req: AgentInvestigationRequest) -> AgentInvestigationResponse:
    doc = None
    if req.document_id:
        doc = backend_state.get_document_by_id(req.document_id)
    if not doc:
        doc = backend_state.get_active_document()

    if not doc:
        raise HTTPException(status_code=400, detail="No active document found to investigate.")

    client = backend_state.get_client()
    agent = ResearchAgent(pdf_processor=doc, gemma_client=client)

    result = agent.run_agentic_investigation(
        user_query=req.query,
        max_steps=req.max_steps or 5,
    )

    return AgentInvestigationResponse(
        query=result["query"],
        execution_trace=result["execution_trace"],
        tool_calls_count=result["tool_calls_count"],
        referenced_pages=result["referenced_pages"],
        synthesized_answer=result["synthesized_answer"],
    )


# ---------------------------------------------------------------------------
# Citations Search Endpoint
# ---------------------------------------------------------------------------
@app.get("/api/documents/{document_id}/citations", response_model=List[Citation])
def get_citations(document_id: str, q: str = Query(...)) -> List[Citation]:
    doc = backend_state.get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    matches = doc.search_pages(q, top_k=4)
    return [
        Citation(
            id=f"SR-{i}",
            title=doc.title,
            page_number=m["page_number"],
            snippet=m["snippet"],
            score=m["score"],
        )
        for i, m in enumerate(matches, 1)
    ]


# ---------------------------------------------------------------------------
# Conversation Sessions Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/conversations", response_model=List[ConversationSession])
def get_conversations() -> List[ConversationSession]:
    res = []
    for cid, cdata in backend_state.conversations.items():
        messages = [ChatMessage(role=m["role"], content=m["content"]) for m in cdata.get("messages", [])]
        res.append(ConversationSession(
            id=cid,
            title=cdata.get("title", "New Research Inquiry"),
            created_at=cdata.get("created_at", ""),
            document_id=cdata.get("document_id"),
            messages=messages,
        ))
    return res


@app.post("/api/conversations", response_model=ConversationSession)
def create_conversation() -> ConversationSession:
    cid = backend_state._create_default_conversation()
    cdata = backend_state.conversations[cid]
    return ConversationSession(
        id=cid,
        title=cdata["title"],
        created_at=cdata["created_at"],
        document_id=cdata["document_id"],
        messages=[],
    )


@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id: str) -> Dict[str, Any]:
    if conversation_id in backend_state.conversations:
        del backend_state.conversations[conversation_id]
        if backend_state.active_conversation_id == conversation_id:
            backend_state._create_default_conversation()
        return {"success": True}
    raise HTTPException(status_code=404, detail="Conversation not found.")


# ---------------------------------------------------------------------------
# Export Endpoint
# ---------------------------------------------------------------------------
@app.post("/api/export")
def export_artifact(req: ExportRequest):
    doc = None
    if req.document_id:
        doc = backend_state.get_document_by_id(req.document_id)
    if not doc:
        doc = backend_state.get_active_document()

    metadata = doc.get_summary_statistics() if doc else None
    title = req.title or (doc.title if doc else "ResearchPilot_Export")

    if req.export_type == "summary":
        md, filename = export_summary_markdown(title, req.content or "", metadata)
    elif req.export_type == "insights":
        md, filename = export_insights_markdown(title, req.content or "", metadata)
    elif req.export_type == "dossier":
        md, filename = export_complete_dossier_markdown(title=title, metadata=metadata, summary=req.content)
    else:
        md = f"# {title}\n\n{req.content or ''}"
        filename = f"{title}.md"

    return Response(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Serve React Frontend Production Build (if available)
# ---------------------------------------------------------------------------
import os
from starlette.staticfiles import StaticFiles

frontend_dist = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
)
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

