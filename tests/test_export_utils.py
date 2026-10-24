"""Unit tests for ResearchPilot AI export utilities and dossier generation."""

import unittest
from src import export_utils


class TestExportUtils(unittest.TestCase):

    def setUp(self):
        self.metadata = {
            "title": "Quantum Error Correction via Surface Codes",
            "filename": "quantum_surface_codes.pdf",
            "page_count": 12,
            "total_words": 6500,
        }

    def test_sanitize_filename(self):
        raw = "Quantum Error Correction: Why / How? <Draft>*"
        clean = export_utils.sanitize_filename(raw)
        self.assertNotIn(":", clean)
        self.assertNotIn("/", clean)
        self.assertNotIn("?", clean)
        self.assertNotIn("<", clean)
        self.assertNotIn("*", clean)
        self.assertIn("Quantum_Error_Correction", clean)

    def test_export_summary_markdown(self):
        summary_body = "### 1. Plain Overview\nWe demonstrate fault-tolerant logical qubits."
        content, filename = export_utils.export_summary_markdown(
            title="Quantum Error Correction",
            summary_content=summary_body,
            metadata=self.metadata,
        )

        self.assertTrue(filename.startswith("ResearchPilot_Summary_"))
        self.assertTrue(filename.endswith(".md"))
        self.assertIn("# Research Summary: Quantum Error Correction", content)
        self.assertIn("quantum_surface_codes.pdf", content)
        self.assertIn("Document Pages:** 12", content)
        self.assertIn(summary_body, content)

    def test_export_chat_markdown(self):
        chat_history = [
            {"role": "user", "content": "What is the threshold error rate?"},
            {"role": "assistant", "content": "The surface code threshold is approximately 1% [PAGE 3]."}
        ]
        content, filename = export_utils.export_chat_markdown(
            title="Quantum Error Correction",
            chat_history=chat_history,
            metadata=self.metadata,
        )

        self.assertTrue(filename.startswith("ResearchPilot_Chat_"))
        self.assertIn("Q&A Notes & Dialogue", content)
        self.assertIn("What is the threshold error rate?", content)
        self.assertIn("approximately 1% [PAGE 3]", content)

    def test_export_insights_markdown(self):
        insights_body = "### Section A: Limitations\nPhysical qubit overhead is significant [PAGE 8]."
        content, filename = export_utils.export_insights_markdown(
            title="Quantum Error Correction",
            insights_content=insights_body,
            metadata=self.metadata,
        )

        self.assertTrue(filename.startswith("ResearchPilot_Insights_"))
        self.assertIn("Research Insights & Opportunities Report", content)
        self.assertIn(insights_body, content)

    def test_export_complete_dossier(self):
        content, filename = export_utils.export_complete_dossier_markdown(
            title="Quantum Error Correction",
            metadata=self.metadata,
            summary="Logical error rate drops exponentially.",
            chat_history=[{"role": "user", "content": "How many physical qubits?"}],
            insights="Research Direction 1: 3D topological codes.",
            figure_notes=[{"page": 4, "question": "Explain Figure 3", "analysis": "Threshold plot."}],
            agent_reports=[{"query": "Find qubit overhead", "tool_calls_count": 3, "synthesized_answer": "Overhead is 1000:1."}],
        )

        self.assertTrue(filename.startswith("ResearchPilot_Full_Dossier_"))
        self.assertIn("# Complete Research Dossier: Quantum Error Correction", content)
        self.assertIn("## 📑 1. Structured Paper Summary", content)
        self.assertIn("## 🧭 2. Research Insights, Limitations & Directions", content)
        self.assertIn("## 🖼️ 3. Visual & Figure Analysis Records", content)
        self.assertIn("## 🤖 4. Autonomous Agent Investigation Traces", content)
        self.assertIn("## 💬 5. Dialogue & Q&A Transcript", content)


if __name__ == "__main__":
    unittest.main()
