"""Unit tests for PDFProcessor using synthetic in-memory PDFs."""

import unittest
try:
    import pymupdf as fitz
except ImportError:
    import fitz

from src.pdf_processor import PDFProcessor, PDFProcessingError


def create_synthetic_pdf(pages_text: list[str], title: str = "Attention Is All You Need") -> bytes:
    """Helper to generate a valid PDF byte buffer in memory."""
    doc = fitz.open()
    doc.set_metadata({"title": title})
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((50, 72), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class TestPDFProcessor(unittest.TestCase):

    def test_valid_pdf_extraction(self):
        pages = [
            "Attention Is All You Need\nAbstract\nWe present the Transformer architecture.",
            "Methodology and Architecture\nThe Transformer uses multi-head self-attention mechanisms.",
            "Experimental Setup and Results\nWe trained on the WMT 2014 English-German dataset. BLEU score is 28.4."
        ]
        pdf_bytes = create_synthetic_pdf(pages, title="Attention Is All You Need")
        proc = PDFProcessor(file_bytes=pdf_bytes, filename="attention.pdf")

        self.assertEqual(proc.page_count, 3)
        self.assertEqual(proc.title, "Attention Is All You Need")
        self.assertFalse(proc.is_scanned)

        is_valid, err = proc.validate_content()
        self.assertTrue(is_valid)
        self.assertIsNone(err)

        full_text = proc.get_full_text()
        self.assertIn("[PAGE 1]", full_text)
        self.assertIn("[PAGE 2]", full_text)
        self.assertIn("[PAGE 3]", full_text)
        self.assertIn("BLEU score is 28.4", full_text)

        # Check section detection
        sections = proc.detected_sections
        self.assertTrue(any(s in sections for s in ["Abstract", "Methodology", "Results"]))

    def test_empty_bytes_raises_error(self):
        with self.assertRaises(PDFProcessingError) as ctx:
            PDFProcessor(file_bytes=b"", filename="empty.pdf")
        self.assertIn("empty", str(ctx.exception).lower())

    def test_invalid_header_raises_error(self):
        with self.assertRaises(PDFProcessingError) as ctx:
            PDFProcessor(file_bytes=b"This is a text file not a PDF", filename="corrupt.pdf")
        self.assertIn("valid pdf header", str(ctx.exception).lower())

    def test_scanned_or_empty_pdf_detection(self):
        # Create a PDF with blank pages (no text inserted)
        doc = fitz.open()
        doc.new_page()
        doc.new_page()
        pdf_bytes = doc.tobytes()
        doc.close()

        proc = PDFProcessor(file_bytes=pdf_bytes, filename="scanned.pdf")
        self.assertTrue(proc.is_scanned)

        is_valid, err = proc.validate_content()
        self.assertFalse(is_valid)
        self.assertIn("scanned document", err.lower())
        self.assertIn("ocr", err.lower())

    def test_page_bounds_and_rendering(self):
        pages = ["Page 1: Overview.", "Page 2: Experiments."]
        pdf_bytes = create_synthetic_pdf(pages)
        proc = PDFProcessor(file_bytes=pdf_bytes)

        # Valid text retrieval
        self.assertIn("Overview", proc.get_page_text(1))
        self.assertIn("Experiments", proc.get_page_text(2))

        # Out-of-bounds raises IndexError
        with self.assertRaises(IndexError):
            proc.get_page_text(0)
        with self.assertRaises(IndexError):
            proc.get_page_text(3)

        # Render page image to PNG
        img_bytes = proc.render_page_image(page_number=1, zoom=1.0)
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 100)
        # PNG signature check: \x89PNG\r\n\x1a\n
        self.assertTrue(img_bytes.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_search_pages(self):
        pages = [
            "Introduction to Neural Machine Translation.",
            "The model utilizes WMT 2014 English-to-German dataset with 4.5 million sentence pairs.",
            "Conclusion and future work in conversational agents."
        ]
        pdf_bytes = create_synthetic_pdf(pages)
        proc = PDFProcessor(file_bytes=pdf_bytes)

        matches = proc.search_pages("WMT dataset sentence pairs", top_k=2)
        self.assertGreater(len(matches), 0)
        top_match = matches[0]
        self.assertEqual(top_match["page_number"], 2)
        self.assertIn("WMT 2014", top_match["snippet"])

    def test_grounded_context_budget(self):
        pages = [f"Page {i} content discussing research details." for i in range(1, 10)]
        pdf_bytes = create_synthetic_pdf(pages)
        proc = PDFProcessor(file_bytes=pdf_bytes)

        ctx = proc.get_grounded_context_for_query("Page 5 details", budget_chars=300)
        self.assertLessEqual(len(ctx), 600)
        self.assertIn("[PAGE", ctx)


if __name__ == "__main__":
    unittest.main()
