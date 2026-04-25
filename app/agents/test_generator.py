"""
Test Data Generator Agent.
Generates comprehensive test data sets based on requirement analysis.
"""

import json

from app.agents.base_agent import BaseAgent
from app.models.schemas import ClarificationResult, TestDataResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

TEST_GEN_SYSTEM_PROMPT = """You are a Senior Test Data Engineering Specialist with deep expertise in software quality assurance.

Your task is to generate comprehensive test data based on a requirement analysis. You receive:
1. The original requirement text
2. A structured analysis identifying missing requirements, ambiguities, and risks

You must generate test data in these categories:

VALID CASES: Realistic test inputs that should be accepted by the system. Cover typical use cases, different user types, and normal workflows.

INVALID CASES: Inputs that should be rejected. Include wrong data types, invalid formats, missing required fields, and out-of-range values.

EDGE CASES: Unusual but legitimate scenarios. Include empty strings, very long inputs, unicode characters, null values, special characters, concurrent operations, and timezone edge cases.

BOUNDARY VALUES: Min/max limits, off-by-one values, exactly-at-limit values. Consider string lengths, numeric ranges, date ranges, and file sizes.

SECURITY CASES: Malicious inputs to test security. Include SQL injection, XSS payloads, path traversal, LDAP injection, command injection, CSRF tokens, and authentication bypass attempts.

For each test case provide:
- scenario: What is being tested
- input: The actual test data/input
- expected: What the system should do

Generate at least 3 cases per category. Be specific and realistic — use actual example data, not generic placeholders."""


SCHEMA_HINT = """{
  "valid_cases": [{"scenario": "string", "input": "string", "expected": "string"}],
  "invalid_cases": [{"scenario": "string", "input": "string", "expected": "string"}],
  "edge_cases": [{"scenario": "string", "input": "string", "expected": "string"}],
  "boundary_values": [{"scenario": "string", "input": "string", "expected": "string"}],
  "security_cases": [{"scenario": "string", "input": "string", "expected": "string"}]
}"""


class TestDataGeneratorAgent(BaseAgent):
    """
    Generates comprehensive test data based on requirement analysis.
    """

    def __init__(self):
        super().__init__(
            name="Test Data Generator Agent",
            system_prompt=TEST_GEN_SYSTEM_PROMPT,
        )

    def generate(
        self,
        requirement_text: str,
        clarification: ClarificationResult,
    ) -> TestDataResult:
        """
        Generate test data based on requirements and clarification analysis.

        Args:
            requirement_text: Original cleaned requirement text
            clarification: Output from the Clarification Agent

        Returns:
            TestDataResult with categorized test data
        """
        logger.info("Starting test data generation")

        # Build combined input for the agent
        combined_input = f"""## ORIGINAL REQUIREMENTS
{requirement_text}

## REQUIREMENT ANALYSIS
Summary: {clarification.summary}

Missing Requirements:
{json.dumps(clarification.missing_requirements, indent=2)}

Ambiguities:
{json.dumps(clarification.ambiguities, indent=2)}

Assumptions:
{json.dumps(clarification.assumptions, indent=2)}

Risk Level: {clarification.risk_level}

## TASK
Based on the above requirements and their analysis, generate comprehensive test data covering all categories."""

        result = self.run(
            user_input=combined_input,
            output_schema=TestDataResult,
            schema_hint=SCHEMA_HINT,
        )

        total_cases = (
            len(result.valid_cases)
            + len(result.invalid_cases)
            + len(result.edge_cases)
            + len(result.boundary_values)
            + len(result.security_cases)
        )

        logger.info(
            f"Test data generation complete: {total_cases} total cases "
            f"(valid={len(result.valid_cases)}, "
            f"invalid={len(result.invalid_cases)}, "
            f"edge={len(result.edge_cases)}, "
            f"boundary={len(result.boundary_values)}, "
            f"security={len(result.security_cases)})"
        )

        return result
