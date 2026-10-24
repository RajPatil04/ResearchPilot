"""System instructions and structured prompts for ResearchPilot AI powered by Gemma 4."""

from __future__ import annotations
from typing import List, Dict, Optional


SYSTEM_INSTRUCTION = (
    "You are ResearchPilot AI, an elite scientific research assistant powered strictly by Gemma 4. "
    "Your mission is to help students, researchers, and engineers understand scientific papers "
    "with uncompromising factual precision and clear scientific reasoning.\n\n"
    "CRITICAL GROUNDING RULES:\n"
    "1. Ground all paper-specific statements exclusively in the supplied paper text and images.\n"
    "2. NEVER invent, hallucinate, or assume authors, publication dates, datasets, baseline metrics, "
    "experimental numbers, citations, or page numbers.\n"
    "3. If a metric, dataset, or claim is not explicitly mentioned in the text, you MUST state: "
    "'Not specified in the provided text.'\n"
    "4. Explicitly distinguish between:\n"
    "   - DIRECT FACTS: Findings, claims, and figures directly reported by the authors.\n"
    "   - INFERENCES: Methodological or conceptual interpretations derived from the text (label as 'Model Inference').\n"
    "   - OPEN HYPOTHESES: New ideas or research opportunities not stated by the authors.\n"
    "5. Whenever citing findings, data, or methodologies, include the corresponding [PAGE N] label "
    "from the extracted document context.\n"
    "6. If the paper does not contain sufficient information to answer a question, state this clearly "
    "rather than fabricating an answer.\n"
    "7. Explain complex mathematical and technical terminology in accessible language without losing precision."
)


def build_summary_prompt(paper_context: str, title: Optional[str] = None) -> str:
    """Builds a structured prompt for comprehensive research paper summarization."""
    header = f"Target Paper: {title}\n" if title else ""
    return f"""{header}Please provide an exhaustive, structured research summary of the paper text provided below.
Strictly adhere to the following 12 sections using clean Markdown headings, bullet points, and paragraphs:

### 1. Paper Title & Overview
- Provide the paper title.
- Give a 2-3 sentence plain-language executive overview accessible to an undergraduate student.

### 2. Research Problem & Motivation
- What specific scientific or engineering problem does this work address?
- Why does this problem matter, and what was the motivation for conducting this research?

### 3. Research Objectives
- What concrete objectives or hypotheses did the authors set out to achieve or test?

### 4. Methodology, Models & Algorithms
- Explain the proposed methodology, framework, or algorithm in structured detail.
- Specify model architectures, loss functions, mathematical formulations, or algorithmic steps mentioned in the text.

### 5. Datasets & Data Sources
- List all datasets, data sources, simulation environments, or benchmarks used.
- Include dataset sizes, data modalities, splits (train/val/test), and preprocessing if reported.
- If not stated, write: "Not specified in the provided text."

### 6. Experimental Setup & Baselines
- Describe the experimental configuration, baseline comparisons, compute resources, and hyperparameter details mentioned.

### 7. Key Findings & Reported Quantitative Results
- Summarize the principal experimental findings.
- Report EXACT numbers, percentages, error rates, or benchmark scores ONLY as stated in the text.
- Do NOT guess or extrapolate metrics.

### 8. Authors' Conclusion
- What are the core conclusions and takeaways drawn directly by the authors?

### 9. Explicit Limitations Reported by Authors
- Detail the limitations and constraints directly acknowledged by the authors.

### 10. Important Terminology Explained
- Select 3 to 5 key technical terms or jargon used in this paper and explain them simply with analogies.

### 11. Model Evaluation & Reflection
- Clearly distinguish the authors' stated claims from what was empirically validated in the text.

### 12. Evidence & Page References Index
- Provide a bulleted index of key sections and their corresponding [PAGE N] references.

---
STRICT RULE: Only use facts from the text below. If any detail is missing, write "Not specified in the provided text."

PAPER EXTRACTED TEXT:
{paper_context}
"""


def build_qa_prompt(
    paper_context: str,
    user_question: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """Builds a conversation-aware question answering prompt."""
    history_formatted = ""
    if chat_history:
        # Include up to the last 6 turns to manage context window
        recent = chat_history[-6:]
        lines = []
        for msg in recent:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "").strip()
            lines.append(f"{role}: {content}")
        history_formatted = "RECENT CONVERSATION HISTORY:\n" + "\n".join(lines) + "\n\n"

    return f"""{history_formatted}USER QUESTION:
{user_question}

INSTRUCTIONS:
1. Answer the question using the extracted paper text below as your primary source of truth.
2. Include specific [PAGE N] references whenever citing facts, figures, or claims.
3. If the paper does NOT contain the answer or enough evidence, state explicitly:
   "The provided text does not contain sufficient information to answer this question."
4. If general background knowledge is needed to clarify a concept, clearly introduce it with:
   "[General Context - Not from Paper]".
5. Never invent experimental numbers, baseline comparisons, or citations.

PAPER EXTRACTED TEXT:
{paper_context}
"""


def build_insights_prompt(paper_context: str) -> str:
    """Builds the prompt for analyzing research opportunities, limitations, and future work."""
    return f"""Analyze the research paper provided below to produce a rigorous 'Research Insights and Opportunities Report'.
Organize your response into the following five structured sections:

### Section A: Explicitly Reported Limitations
- List every limitation, bottleneck, boundary condition, or failure case explicitly acknowledged by the authors.
- Cite the exact [PAGE N] where each limitation is mentioned.

### Section B: Potentially Inferred Limitations (Methodological & Evaluative)
- Identify realistic limitations or blind spots reasonably inferred from the described methodology, dataset characteristics, evaluation protocol, or theoretical assumptions.
- Must be explicitly labeled as: "[Model Inference - Not stated by authors]".

### Section C: Potential Research Gaps & Proposed Research Directions
Suggest 3 to 5 actionable, high-impact research directions that logically build upon this paper.
For EACH research direction, provide:
1. **Research Question**: A clear, testable scientific or engineering question.
2. **Motivation & Connection**: Why this matters and how it directly bridges a gap in this paper.
3. **Proposed Methodology**: Concrete algorithmic, theoretical, or experimental approach.
4. **Suggested Experiment**: Experimental setup, datasets to test on, and baseline comparisons.
5. **Evaluation Metrics**: Specific metrics to measure success.
6. **Anticipated Challenges**: Technical, computational, or theoretical hurdles.
7. **Hypothesis Testing**: What specific evidence or results would support or refute this hypothesis?
*(Note: A full literature review is required to guarantee novelty).*

### Section D: Author-Proposed Future Work
- Summarize future work and next steps explicitly suggested by the authors.
- Keep this strictly separate from Section C.

### Section E: Research Reliability & Evidence Assessment
- Assess where the paper lacks sufficient data, ablation studies, baseline comparisons, or error bounds to support a definitive conclusion.
- Note any potential risks of bias, dataset distribution shift, or reproducibility challenges.

---
PAPER EXTRACTED TEXT:
{paper_context}
"""


def build_figure_analysis_prompt(
    user_question: str,
    page_number: int,
    page_text: Optional[str] = None
) -> str:
    """Builds the prompt for multimodal visual inspection of figures, charts, and diagrams."""
    text_context = ""
    if page_text and page_text.strip():
        text_context = f"\nEXTRACTED TEXT FROM THIS PAGE (Page {page_number}):\n{page_text[:4000]}\n"

    return f"""You are visually inspecting a rendered page (Page {page_number}) from a scientific research paper.

USER INQUIRY:
{user_question}
{text_context}
INSTRUCTIONS FOR VISUAL ANALYSIS:
1. Break down what is visually present (e.g., architecture diagram, flow chart, bar chart, loss curve, scatter plot, comparison table).
2. For charts and graphs:
   - Identify the X-axis, Y-axis, legends, and units.
   - Describe observable trends, inflection points, or comparative baselines.
   - If labels, numbers, or tick marks are blurred, small, or unreadable, explicitly state:
     "[Unreadable Label/Value: cannot determine with certainty]". Do NOT guess missing numbers.
3. For architectural/system diagrams:
   - Identify components, input/output tensors, arrow flow, and sub-modules.
4. Distinguish between DIRECT VISUAL OBSERVATIONS (what is plainly visible) and INTERPRETATION (what the trend or design signifies).
5. Ground your explanation in the accompanying page text when available.
"""


def build_agent_tool_selection_prompt(user_query: str, paper_stats: Dict) -> str:
    """Prompt for the agent to determine the optimal investigation workflow."""
    return f"""You are an autonomous research agent investigating a scientific paper.
PAPER SUMMARY STATS:
- Title: {paper_stats.get('title', 'Unknown')}
- Total Pages: {paper_stats.get('page_count', 0)}
- Total Words: {paper_stats.get('total_words', 0)}
- Sections: {', '.join(paper_stats.get('sections_detected', []))}

USER INQUIRY:
{user_query}

Plan the optimal research inquiry steps to answer this inquiry with evidence.
"""
