"""
Requirement Clarification Agent.
Analyzes requirement text to identify gaps, ambiguities, and risks.
"""

from app.agents.base_agent import BaseAgent
from app.models.schemas import ClarificationResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

CLARIFIER_SYSTEM_PROMPT = """You are a Senior QA Requirements Analyst with 15+ years of experience in enterprise software.

Your task is to analyze software requirement documents and provide a thorough quality assessment.

You must:
1. Write a concise SUMMARY of the requirements
2. Identify MISSING REQUIREMENTS — things that should be specified but aren't (e.g., error handling, performance criteria, security requirements, accessibility, data validation rules, concurrency behavior)
3. Detect AMBIGUITIES — statements that can be interpreted in multiple ways (e.g., "the system should be fast", "users can manage their data")
4. Generate CLARIFICATION QUESTIONS — specific questions that should be asked to stakeholders to fill the gaps
5. Extract ASSUMPTIONS — things you assume to be true based on context but that aren't explicitly stated
6. Assess RISK LEVEL — overall risk of proceeding with these requirements as-is:
   - "low": Requirements are mostly clear, minor gaps only
   - "medium": Some important details are missing or ambiguous
   - "high": Multiple critical gaps that could lead to significant rework
   - "critical": Requirements are too vague to begin implementation

Be thorough but practical. Focus on issues that would actually cause problems during development and testing."""


SCHEMA_HINT = """{
  "summary": "string — concise summary of the requirements",
  "missing_requirements": ["string — each missing requirement"],
  "ambiguities": ["string — each ambiguous statement"],
  "clarification_questions": ["string — each question for stakeholders"],
  "assumptions": ["string — each assumption made"],
  "risk_level": "string — one of: low, medium, high, critical"
}"""


class ClarificationAgent(BaseAgent):
    """
    Analyzes requirement text and produces structured clarification output.
    """

    def __init__(self):
        super().__init__(
            name="Requirement Clarification Agent",
            system_prompt=CLARIFIER_SYSTEM_PROMPT,
        )

    def analyze(self, requirement_text: str) -> ClarificationResult:
        """
        Analyze requirement text for gaps, ambiguities, and risks.

        Args:
            requirement_text: Cleaned requirement text from the PDF

        Returns:
            ClarificationResult with structured analysis
        """
        logger.info(f"Starting requirement analysis ({len(requirement_text)} chars)")

        result = self.run(
            user_input=requirement_text,
            output_schema=ClarificationResult,
            schema_hint=SCHEMA_HINT,
        )

        logger.info(
            f"Analysis complete: risk_level={result.risk_level}, "
            f"missing={len(result.missing_requirements)}, "
            f"ambiguities={len(result.ambiguities)}, "
            f"questions={len(result.clarification_questions)}"
        )

        return result
