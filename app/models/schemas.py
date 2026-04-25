"""
Pydantic schemas for structured agent outputs.
Enforces JSON contracts between pipeline stages.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ClarificationResult(BaseModel):
    """Output schema for the Requirement Clarification Agent."""

    summary: str = Field(
        description="High-level summary of the requirements analysis"
    )
    missing_requirements: list[str] = Field(
        default_factory=list,
        description="List of requirements that are missing or underspecified"
    )
    ambiguities: list[str] = Field(
        default_factory=list,
        description="List of ambiguous statements found in the requirements"
    )
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Questions that should be asked to stakeholders"
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made while analyzing the requirements"
    )
    risk_level: str = Field(
        description="Overall risk level: 'low', 'medium', 'high', or 'critical'"
    )


class TestCase(BaseModel):
    """Individual test case with scenario, input, and expected result."""

    scenario: str = Field(description="Description of the test scenario")
    input: str = Field(description="Test input data")
    expected: str = Field(description="Expected result or behavior")


class TestDataResult(BaseModel):
    """Output schema for the Test Data Generator Agent."""

    valid_cases: list[TestCase] = Field(
        default_factory=list,
        description="Test cases with valid input data"
    )
    invalid_cases: list[TestCase] = Field(
        default_factory=list,
        description="Test cases with invalid input data"
    )
    edge_cases: list[TestCase] = Field(
        default_factory=list,
        description="Edge case scenarios"
    )
    boundary_values: list[TestCase] = Field(
        default_factory=list,
        description="Boundary value test cases"
    )
    security_cases: list[TestCase] = Field(
        default_factory=list,
        description="Security-related test cases (injection, XSS, etc.)"
    )


class PipelineResult(BaseModel):
    """Complete pipeline output combining all agent results."""

    pdf_filename: str = Field(description="Name of the uploaded PDF file")
    extracted_text: str = Field(description="Cleaned text extracted from the PDF")
    clarification: ClarificationResult = Field(
        description="Output from the Requirement Clarification Agent"
    )
    test_data: TestDataResult = Field(
        description="Output from the Test Data Generator Agent"
    )
    processing_time_seconds: float = Field(
        description="Total pipeline execution time in seconds"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp of when the analysis was completed"
    )


class HealthStatus(BaseModel):
    """Health check response."""

    status: str
    ollama_connected: bool
    model_available: bool
    model_name: str
