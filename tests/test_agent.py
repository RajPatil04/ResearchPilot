"""Unit tests for ResearchAgent tool execution, safety boundaries, and trace logging."""

import unittest
from src.pdf_processor import PDFProcessor
from src.research_agent import ResearchAgent, ToolExecutionError
from tests.test_pdf_processor import create_synthetic_pdf


class TestResearchAgent(unittest.TestCase):

    def setUp(self):
        pages = [
            "ResearchPilot AI Paper\nAbstract\nAutonomous agents for literature understanding.",
            "Methodology\nWe register 5 tools for reading and analyzing PDF structures.",
            "Evaluation\nAccuracy is 94.2% on standard benchmarks with zero hallucinated tools."
        ]
        pdf_bytes = create_synthetic_pdf(pages, title="Agent Investigation Test")
        self.proc = PDFProcessor(file_bytes=pdf_bytes, filename="agent_test.pdf")
        self.agent = ResearchAgent(pdf_processor=self.proc, gemma_client=None)

    def test_registered_tools_execution(self):
        # 1. Metadata tool
        res_meta = self.agent.execute_registered_tool("get_paper_metadata")
        self.assertTrue(res_meta["success"])
        self.assertEqual(res_meta["data"]["page_count"], 3)
        self.assertEqual(res_meta["data"]["title"], "Agent Investigation Test")

        # 2. Page text tool
        res_page = self.agent.execute_registered_tool("get_page_text", page_number=2)
        self.assertTrue(res_page["success"])
        self.assertIn("register 5 tools", res_page["data"]["content"])

        # 3. Search tool
        res_search = self.agent.execute_registered_tool("search_paper_text", query="Accuracy benchmark", top_k=2)
        self.assertTrue(res_search["success"])
        self.assertEqual(res_search["data"]["matches_found"], 1)

        # 4. Statistics tool
        res_stats = self.agent.execute_registered_tool("get_paper_statistics")
        self.assertTrue(res_stats["success"])
        self.assertEqual(res_stats["data"]["page_count"], 3)

        # 5. Render page info tool
        res_render = self.agent.execute_registered_tool("render_pdf_page", page_number=1)
        self.assertTrue(res_render["success"])
        self.assertEqual(res_render["data"]["image_format"], "PNG")

    def test_unauthorized_tool_rejected(self):
        with self.assertRaises(ToolExecutionError) as ctx:
            self.agent.execute_registered_tool("execute_shell_command", command="dir")
        self.assertIn("Unauthorized or unknown tool", str(ctx.exception))

    def test_page_bounds_validation(self):
        # Invalid page number should fail safely without crashing
        res_bad = self.agent.execute_registered_tool("get_page_text", page_number=999)
        self.assertFalse(res_bad["success"])
        self.assertIn("out of bounds", res_bad["error"].lower())

    def test_empty_search_validation(self):
        res_empty = self.agent.execute_registered_tool("search_paper_text", query="")
        self.assertFalse(res_empty["success"])
        self.assertIn("empty", res_empty["error"].lower())

    def test_agent_investigation_workflow_and_trace(self):
        result = self.agent.run_agentic_investigation(
            user_query="What was the reported benchmark accuracy?",
            max_steps=5
        )

        self.assertIn("query", result)
        self.assertIn("execution_trace", result)
        self.assertGreater(result["tool_calls_count"], 0)
        self.assertIsInstance(result["execution_trace"], list)

        # Verify trace structure
        trace = result["execution_trace"]
        tool_names = [step["tool"] for step in trace]
        self.assertIn("get_paper_metadata", tool_names)
        self.assertIn("search_paper_text", tool_names)

        # Verify synthesis message mentions pages
        self.assertIn("Agent investigation completed", result["synthesized_answer"])


if __name__ == "__main__":
    unittest.main()
