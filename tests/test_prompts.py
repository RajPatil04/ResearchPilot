"""Unit tests for ResearchPilot AI prompt engineering and constraints."""

import unittest
from src import prompts


class TestPrompts(unittest.TestCase):

    def test_system_instruction_grounding_rules(self):
        sys_inst = prompts.SYSTEM_INSTRUCTION
        self.assertIn("ResearchPilot AI", sys_inst)
        self.assertIn("Gemma 4", sys_inst)
        self.assertIn("NEVER invent, hallucinate, or assume", sys_inst)
        self.assertIn("Not specified in the provided text.", sys_inst)
        self.assertIn("[PAGE N]", sys_inst)

    def test_summary_prompt_structure(self):
        context = "[PAGE 1]\nIntroduction\n[PAGE 2]\nMethodology\n[PAGE 3]\nResults"
        prompt = prompts.build_summary_prompt(context, title="Transformer Architecture")

        self.assertIn("Transformer Architecture", prompt)
        self.assertIn("1. Paper Title & Overview", prompt)
        self.assertIn("2. Research Problem & Motivation", prompt)
        self.assertIn("4. Methodology, Models & Algorithms", prompt)
        self.assertIn("5. Datasets & Data Sources", prompt)
        self.assertIn("7. Key Findings & Reported Quantitative Results", prompt)
        self.assertIn("9. Explicit Limitations Reported by Authors", prompt)
        self.assertIn("12. Evidence & Page References Index", prompt)
        self.assertIn("Not specified in the provided text.", prompt)
        self.assertIn(context, prompt)

    def test_qa_prompt_with_and_without_history(self):
        context = "[PAGE 1]\nAttention mechanisms allow modeling dependencies."
        q = "Why use attention instead of recurrence?"

        # Without history
        prompt_no_hist = prompts.build_qa_prompt(context, q)
        self.assertIn(q, prompt_no_hist)
        self.assertIn(context, prompt_no_hist)
        self.assertNotIn("RECENT CONVERSATION HISTORY", prompt_no_hist)

        # With history
        history = [
            {"role": "user", "content": "What is self-attention?"},
            {"role": "assistant", "content": "Self-attention relates different positions of a single sequence."}
        ]
        prompt_with_hist = prompts.build_qa_prompt(context, q, chat_history=history)
        self.assertIn("RECENT CONVERSATION HISTORY:", prompt_with_hist)
        self.assertIn("What is self-attention?", prompt_with_hist)
        self.assertIn("Self-attention relates different positions", prompt_with_hist)
        self.assertIn(q, prompt_with_hist)

    def test_insights_prompt_structure(self):
        context = "[PAGE 1]\nExperiments performed on 8 GPUs."
        prompt = prompts.build_insights_prompt(context)

        self.assertIn("Section A: Explicitly Reported Limitations", prompt)
        self.assertIn("Section B: Potentially Inferred Limitations", prompt)
        self.assertIn("Section C: Potential Research Gaps & Proposed Research Directions", prompt)
        self.assertIn("Section D: Author-Proposed Future Work", prompt)
        self.assertIn("Section E: Research Reliability & Evidence Assessment", prompt)
        self.assertIn(context, prompt)

    def test_figure_analysis_prompt(self):
        prompt = prompts.build_figure_analysis_prompt(
            user_question="Explain the attention heads matrix.",
            page_number=4,
            page_text="Figure 2 shows multi-head attention."
        )
        self.assertIn("Page 4", prompt)
        self.assertIn("Explain the attention heads matrix.", prompt)
        self.assertIn("Figure 2 shows multi-head attention.", prompt)
        self.assertIn("Do NOT guess missing numbers.", prompt)


if __name__ == "__main__":
    unittest.main()
