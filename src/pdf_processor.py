"""PDF processing and text extraction module for ResearchPilot AI using PyMuPDF (fitz)."""

from __future__ import annotations

import re
try:
    import pymupdf as fitz
except ImportError:
    import fitz
from typing import Any, Dict, List, Optional, Tuple


class PDFProcessingError(Exception):
    """Raised when PDF validation or extraction fails."""
    pass


class PDFProcessor:
    """Extracts, indexes, and manages content from PDF research papers.
    
    Operates strictly locally without transmitting files to third parties during parsing.
    """

    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit
    DEFAULT_MAX_CONTEXT_CHARS = 55000       # Safe context window budget for Gemma 4

    def __init__(self, file_bytes: bytes, filename: str = "document.pdf"):
        if not file_bytes:
            raise PDFProcessingError("Uploaded file is empty (0 bytes). Please upload a valid PDF.")

        if len(file_bytes) > self.MAX_FILE_SIZE_BYTES:
            size_mb = len(file_bytes) / (1024 * 1024)
            raise PDFProcessingError(
                f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of 50 MB."
            )

        # Magic number check for PDF (%PDF-)
        if not file_bytes.startswith(b"%PDF-"):
            raise PDFProcessingError("The uploaded file does not have a valid PDF header (%PDF-).")

        self.filename = filename
        self.file_size = len(file_bytes)
        self.raw_bytes = file_bytes

        try:
            self.doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:
            raise PDFProcessingError(f"Could not open or parse PDF document: {exc}")

        if self.doc.is_encrypted:
            raise PDFProcessingError(
                "This PDF is password-protected or encrypted. Please decrypt it before uploading."
            )

        self.page_count = len(self.doc)
        if self.page_count == 0:
            raise PDFProcessingError("The PDF contains 0 pages.")

        self.pages: List[Dict[str, Any]] = []
        self._extract_all_pages()
        self.title = self._detect_title()
        self.detected_sections = self._detect_sections()

    def _extract_all_pages(self) -> None:
        """Extract text page by page with explicit boundary indexing."""
        total_chars = 0
        total_words = 0

        for idx in range(self.page_count):
            page = self.doc[idx]
            page_text = page.get_text("text") or ""
            # Clean non-printable / null characters
            page_text = page_text.replace("\x00", "").strip()

            words = len(page_text.split())
            chars = len(page_text)
            total_chars += chars
            total_words += words

            self.pages.append({
                "page_number": idx + 1,
                "text": page_text,
                "char_count": chars,
                "word_count": words,
            })

        self.total_chars = total_chars
        self.total_words = total_words
        self.is_scanned = (total_chars < 50 or total_words < 15)

    def validate_content(self) -> Tuple[bool, Optional[str]]:
        """Checks if the document contains extractable text.
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message_if_invalid)
        """
        if self.is_scanned:
            return False, (
                "No selectable text was found in this PDF. It appears to be a scanned document "
                "or image-only PDF. ResearchPilot AI requires text-based PDFs; optical character "
                "recognition (OCR) is required before processing scanned documents."
            )
        return True, None

    def _detect_title(self) -> str:
        """Extracts the paper title from metadata or Page 1 content."""
        meta_title = self.doc.metadata.get("title", "") if self.doc.metadata else ""
        if meta_title and len(meta_title.strip()) > 4:
            clean = meta_title.strip()
            # Filter generic title defaults
            if not re.search(r"^(untitled|microsoft word|pdf document|default)$", clean, re.I):
                return clean

        # Inspect Page 1 text blocks
        if self.pages and self.pages[0]["text"]:
            page_1_text = self.pages[0]["text"]
            lines = [line.strip() for line in page_1_text.splitlines() if line.strip()]
            for line in lines[:5]:
                # Skip common arXiv or header notices
                if re.search(r"^(arxiv|submitted to|accepted at|conference|journal|preprint|volume|issn|doi)", line, re.I):
                    continue
                if len(line.split()) >= 3 and len(line) < 220:
                    return line

        return self.filename.replace(".pdf", "").replace("_", " ").title()

    def _detect_sections(self) -> List[str]:
        """Scans extracted text for common scientific research paper section headings."""
        known_sections = [
            "Abstract",
            "Introduction",
            "Background",
            "Related Work",
            "Methodology",
            "Method",
            "Architecture",
            "Experiments",
            "Experimental Setup",
            "Results",
            "Evaluation",
            "Discussion",
            "Limitations",
            "Conclusion",
            "Future Work",
            "References"
        ]
        found = []
        combined_text = "\n".join(p["text"][:1000] for p in self.pages[:min(10, len(self.pages))])
        for sec in known_sections:
            pattern = rf"(?i)\b(?:[0-9]\.?\s*)?{re.escape(sec)}\b"
            if re.search(pattern, combined_text):
                found.append(sec)
        return found

    def get_full_text(self, max_chars: Optional[int] = None) -> str:
        """Assembles all pages with explicit [PAGE N] headers."""
        formatted_pages = [
            f"[PAGE {p['page_number']}]\n{p['text']}"
            for p in self.pages
            if p["text"]
        ]
        full = "\n\n".join(formatted_pages)
        if max_chars and len(full) > max_chars:
            return full[:max_chars]
        return full

    def get_page_text(self, page_number: int) -> str:
        """Retrieves text for a specific 1-indexed page."""
        if not (1 <= page_number <= self.page_count):
            raise IndexError(f"Page number {page_number} is out of bounds (1-{self.page_count}).")
        return self.pages[page_number - 1]["text"]

    def render_page_image(self, page_number: int, zoom: float = 1.5) -> bytes:
        """Renders a PDF page to high-quality PNG bytes for visual analysis."""
        if not (1 <= page_number <= self.page_count):
            raise IndexError(f"Page number {page_number} is out of bounds (1-{self.page_count}).")

        page = self.doc[page_number - 1]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        return pix.tobytes("png")

    def search_pages(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Performs lexical search across pages to locate relevant evidence."""
        if not query or not query.strip():
            return []

        # Tokenize query
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "in", "on", "at", "to", "for", "of", "with"}
        tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2 and t.lower() not in stop_words]
        if not tokens:
            tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 1]

        results = []
        for p in self.pages:
            text_lower = p["text"].lower()
            score = 0
            snippet = ""
            for token in tokens:
                count = text_lower.count(token)
                score += count

            if score > 0:
                # Find best snippet around first matching token
                first_pos = -1
                for token in tokens:
                    pos = text_lower.find(token)
                    if pos != -1 and (first_pos == -1 or pos < first_pos):
                        first_pos = pos

                if first_pos != -1:
                    start = max(0, first_pos - 120)
                    end = min(len(p["text"]), first_pos + 260)
                    snippet = p["text"][start:end].replace("\n", " ").strip()
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(p["text"]):
                        snippet = snippet + "..."

                results.append({
                    "page_number": p["page_number"],
                    "score": score,
                    "snippet": snippet,
                    "char_count": p["char_count"]
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_grounded_context_for_query(self, query: str, budget_chars: int = DEFAULT_MAX_CONTEXT_CHARS) -> str:
        """Constructs an evidence-focused context budget.
        
        If the entire paper fits within the budget, returns the full document.
        Otherwise, prioritizes Page 1 (Abstract/Intro) + the most relevant pages
        containing search terms, ensuring grounded context without truncating critical parts.
        """
        full = self.get_full_text()
        if len(full) <= budget_chars:
            return full

        # Paper exceeds budget: build smart selective context
        matches = self.search_pages(query, top_k=6)
        matched_page_numbers = {m["page_number"] for m in matches}
        # Always include page 1 (Abstract/Intro) and final page (often Conclusion)
        selected_pages = {1, self.page_count} | matched_page_numbers

        chunks = []
        current_len = 0
        for page_num in sorted(selected_pages):
            p_text = self.get_page_text(page_num)
            formatted = f"[PAGE {page_num}]\n{p_text}"
            if current_len + len(formatted) < budget_chars:
                chunks.append(formatted)
                current_len += len(formatted)
            else:
                remaining = budget_chars - current_len
                if remaining > 500:
                    chunks.append(formatted[:remaining] + "\n...[Content truncated to preserve budget]...")
                break

        header = (
            f"Note: This paper contains {self.page_count} pages ({len(full):,} characters). "
            f"Below is a grounded context selection focusing on Pages "
            f"{', '.join(str(p) for p in sorted(selected_pages))} relevant to your inquiry.\n\n"
        )
        return header + "\n\n".join(chunks)

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Returns structured document statistics."""
        return {
            "title": self.title,
            "filename": self.filename,
            "page_count": self.page_count,
            "total_characters": self.total_chars,
            "total_words": self.total_words,
            "estimated_reading_minutes": round(self.total_words / 200, 1) if self.total_words else 0,
            "is_scanned": self.is_scanned,
            "sections_detected": self.detected_sections,
            "file_size_kb": round(self.file_size / 1024, 1),
        }
