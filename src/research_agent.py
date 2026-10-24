"""Lightweight agentic research assistant workflow with tool execution and trace logging."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional
from src.pdf_processor import PDFProcessor
from src.gemma_client import GemmaClient


class ToolExecutionError(Exception):
    """Raised when a registered tool fails during execution."""
    pass


class ResearchAgent:
    """Safe, bounded autonomous research agent for deep paper investigations.
    
    Executes only registered, read-only tools against the loaded PDF processor.
    Never executes arbitrary code, shell commands, or file system writes.
    """

    def __init__(self, pdf_processor: PDFProcessor, gemma_client: Optional[GemmaClient] = None):
        self.processor = pdf_processor
        self.gemma = gemma_client
        self.execution_trace: List[Dict[str, Any]] = []

        # Explicitly registered, validated tools
        self._tools: Dict[str, Callable[..., Any]] = {
            "get_paper_metadata": self._tool_get_metadata,
            "get_page_text": self._tool_get_page_text,
            "search_paper_text": self._tool_search_text,
            "get_paper_statistics": self._tool_get_statistics,
            "render_pdf_page": self._tool_render_page_info,
        }

    def _tool_get_metadata(self) -> Dict[str, Any]:
        """Tool: Returns high-level paper metadata."""
        stats = self.processor.get_summary_statistics()
        return {
            "title": stats["title"],
            "filename": stats["filename"],
            "page_count": stats["page_count"],
            "total_words": stats["total_words"],
            "sections_detected": stats["sections_detected"],
            "is_scanned": stats["is_scanned"]
        }

    def _tool_get_page_text(self, page_number: int) -> Dict[str, Any]:
        """Tool: Returns text of a specific 1-indexed page."""
        try:
            p_num = int(page_number)
        except (ValueError, TypeError):
            raise ToolExecutionError(f"Invalid page number argument: '{page_number}'. Must be an integer.")

        if p_num < 1 or p_num > self.processor.page_count:
            raise ToolExecutionError(
                f"Page {p_num} is out of bounds. The paper contains {self.processor.page_count} pages."
            )

        text = self.processor.get_page_text(p_num)
        return {
            "page_number": p_num,
            "char_count": len(text),
            "word_count": len(text.split()),
            "content": text
        }

    def _tool_search_text(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Tool: Searches paper for keywords and returns matching page snippets."""
        if not query or not str(query).strip():
            raise ToolExecutionError("Search query cannot be empty.")

        matches = self.processor.search_pages(str(query), top_k=int(top_k))
        return {
            "query": str(query),
            "matches_found": len(matches),
            "results": matches
        }

    def _tool_get_statistics(self) -> Dict[str, Any]:
        """Tool: Returns detailed structural and length statistics."""
        return self.processor.get_summary_statistics()

    def _tool_render_page_info(self, page_number: int) -> Dict[str, Any]:
        """Tool: Confirms page rendering readiness and dimensions for visual analysis."""
        try:
            p_num = int(page_number)
        except (ValueError, TypeError):
            raise ToolExecutionError(f"Invalid page number: '{page_number}'.")

        if p_num < 1 or p_num > self.processor.page_count:
            raise ToolExecutionError(f"Page {p_num} is out of bounds (1-{self.processor.page_count}).")

        img_bytes = self.processor.render_page_image(p_num, zoom=1.0)
        return {
            "page_number": p_num,
            "image_format": "PNG",
            "byte_size": len(img_bytes),
            "status": "Rendered successfully"
        }

    def execute_registered_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Executes a strictly registered tool with bounds checking and error handling."""
        if tool_name not in self._tools:
            raise ToolExecutionError(
                f"Unauthorized or unknown tool: '{tool_name}'. Registered tools are: {list(self._tools.keys())}"
            )

        try:
            result = self._tools[tool_name](**kwargs)
            return {"success": True, "data": result}
        except ToolExecutionError as te:
            return {"success": False, "error": str(te)}
        except Exception as exc:
            return {"success": False, "error": f"Tool execution failed: {str(exc)}"}

    def run_agentic_investigation(
        self,
        user_query: str,
        max_steps: int = 5
    ) -> Dict[str, Any]:
        """Autonomous, bounded multi-step evidence gathering and synthesis.
        
        1. Formulates search and inspection targets.
        2. Executes tools sequentially, logging every step.
        3. Gathers grounded evidence snippets.
        4. Invokes Gemma 4 to synthesize a final answer grounded in the discovered tool evidence.
        """
        self.execution_trace.clear()
        collected_evidence: List[str] = []
        referenced_pages: List[int] = []

        # Step 1: Inspect paper metadata
        step_1 = self.execute_registered_tool("get_paper_metadata")
        self.execution_trace.append({
            "step": 1,
            "tool": "get_paper_metadata",
            "args": {},
            "status": "success" if step_1["success"] else "error",
            "summary": f"Inspected paper metadata ({step_1.get('data', {}).get('page_count', 0)} pages, {step_1.get('data', {}).get('total_words', 0)} words)"
        })

        # Step 2: Search for relevant passages matching inquiry
        search_res = self.execute_registered_tool("search_paper_text", query=user_query, top_k=3)
        matches = search_res.get("data", {}).get("results", []) if search_res["success"] else []
        self.execution_trace.append({
            "step": 2,
            "tool": "search_paper_text",
            "args": {"query": user_query, "top_k": 3},
            "status": "success" if search_res["success"] else "error",
            "summary": f"Identified {len(matches)} relevant page(s): {[m['page_number'] for m in matches]}"
        })

        # Step 3: Fetch full text of top matching pages (up to 2 pages to keep request bounded)
        target_pages = [m["page_number"] for m in matches[:2]]
        if not target_pages:
            # Default to page 1 (Abstract / Intro)
            target_pages = [1]

        for p_num in target_pages:
            if len(self.execution_trace) >= max_steps:
                break
            page_res = self.execute_registered_tool("get_page_text", page_number=p_num)
            if page_res["success"]:
                content = page_res["data"]["content"]
                collected_evidence.append(f"[PAGE {p_num}]\n{content}")
                referenced_pages.append(p_num)
                self.execution_trace.append({
                    "step": len(self.execution_trace) + 1,
                    "tool": "get_page_text",
                    "args": {"page_number": p_num},
                    "status": "success",
                    "summary": f"Retrieved full text of Page {p_num} ({len(content)} chars)"
                })

        # Synthesize final answer using Gemma 4 if client is attached
        evidence_block = "\n\n".join(collected_evidence)
        synthesized_text = ""

        if self.gemma:
            prompt = (
                f"You are ResearchPilot AI, an agent that just completed an evidence-gathering run on this paper.\n\n"
                f"USER INVESTIGATION INQUIRY: {user_query}\n\n"
                f"PAGES RETRIEVED BY AGENT TOOLS: {referenced_pages}\n\n"
                f"COLLECTED EVIDENCE:\n{evidence_block}\n\n"
                f"INSTRUCTIONS:\n"
                f"Synthesize a clear, grounded answer to the user's inquiry based strictly on the retrieved evidence above.\n"
                f"Cite the relevant [PAGE N] for all claims.\n"
                f"If the retrieved evidence does not contain sufficient information, state that clearly.\n"
                f"Do not invent facts, numbers, or citations."
            )
            try:
                synthesized_text = self.gemma.generate_text(prompt=prompt)
            except Exception as exc:
                synthesized_text = f"Agent inquiry synthesis failed: {exc}"
        else:
            synthesized_text = (
                f"Agent investigation completed. Retrieved evidence from Pages {referenced_pages}. "
                "Connect a live Gemma 4 API key to enable AI answer synthesis."
            )

        return {
            "query": user_query,
            "execution_trace": self.execution_trace,
            "tool_calls_count": len(self.execution_trace),
            "referenced_pages": referenced_pages,
            "evidence_snippets": [m.get("snippet", "") for m in matches if m.get("snippet")],
            "synthesized_answer": synthesized_text
        }
