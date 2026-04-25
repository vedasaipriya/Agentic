"""
Base agent class.
Provides common LLM interaction patterns including prompt construction,
JSON parsing, schema validation, and retry logic.
"""

import json
import re
from typing import Type, TypeVar

from langchain_ollama import OllamaLLM
from pydantic import BaseModel, ValidationError

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_RETRIES, LLM_TEMPERATURE, LLM_REQUEST_TIMEOUT
from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    """
    Base class for all AI agents.

    Handles LLM initialization, prompt formatting, JSON extraction,
    schema validation, and retry logic with error feedback.
    """

    def __init__(self, name: str, system_prompt: str):
        """
        Initialize the base agent.

        Args:
            name: Human-readable agent name for logging
            system_prompt: System-level instructions for the LLM
        """
        self.name = name
        self.system_prompt = system_prompt
        self.llm = OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=LLM_TEMPERATURE,
            timeout=LLM_REQUEST_TIMEOUT,
        )
        logger.info(f"Agent '{self.name}' initialized with model: {OLLAMA_MODEL}")

    def _build_prompt(self, user_input: str, schema_hint: str = "") -> str:
        """
        Build the full prompt combining system prompt, schema hint, and user input.

        Args:
            user_input: The user's input text
            schema_hint: JSON schema description for the expected output

        Returns:
            Formatted prompt string
        """
        prompt = f"""### SYSTEM
{self.system_prompt}

### OUTPUT FORMAT
You MUST respond with ONLY a valid JSON object. No markdown, no code fences, no explanation.
{schema_hint}

### INPUT
{user_input}

### RESPONSE (valid JSON only):"""
        return prompt

    def _extract_json(self, raw_response: str) -> dict:
        """
        Extract a JSON object from the LLM's raw response.
        Handles cases where the LLM wraps JSON in markdown code fences.

        Args:
            raw_response: Raw text response from the LLM

        Returns:
            Parsed JSON as a dictionary

        Raises:
            ValueError: If no valid JSON can be extracted
        """
        text = raw_response.strip()

        # Try direct JSON parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code fences
        patterns = [
            r"```json\s*\n(.*?)\n\s*```",
            r"```\s*\n(.*?)\n\s*```",
            r"\{.*\}",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if match.lastindex else match.group(0)
                    return json.loads(json_str)
                except (json.JSONDecodeError, IndexError):
                    continue

        raise ValueError(f"Could not extract valid JSON from response: {text[:200]}...")

    def run(
        self,
        user_input: str,
        output_schema: Type[T],
        schema_hint: str = "",
    ) -> T:
        """
        Execute the agent with retry logic and schema validation.

        Args:
            user_input: Input text for the agent to process
            output_schema: Pydantic model class for validating the output
            schema_hint: Description of the expected JSON structure

        Returns:
            Validated Pydantic model instance

        Raises:
            RuntimeError: If all retries are exhausted
        """
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"[{self.name}] Attempt {attempt}/{MAX_RETRIES}")

            try:
                # Build prompt (include previous error feedback on retries)
                error_context = ""
                if last_error and attempt > 1:
                    error_context = (
                        f"\n\n### PREVIOUS ERROR\n"
                        f"Your previous response had this error: {last_error}\n"
                        f"Please fix this and return valid JSON.\n"
                    )

                prompt = self._build_prompt(
                    user_input + error_context,
                    schema_hint
                )

                logger.debug(f"[{self.name}] Prompt length: {len(prompt)} chars")

                # Call LLM
                raw_response = self.llm.invoke(prompt)
                logger.debug(
                    f"[{self.name}] Response length: {len(raw_response)} chars"
                )

                # Extract JSON
                json_data = self._extract_json(raw_response)

                # Validate against schema
                result = output_schema.model_validate(json_data)
                logger.info(f"[{self.name}] Success on attempt {attempt}")
                return result

            except (ValueError, ValidationError, json.JSONDecodeError) as e:
                last_error = str(e)
                logger.warning(
                    f"[{self.name}] Attempt {attempt} failed: {last_error}"
                )

            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"[{self.name}] Unexpected error on attempt {attempt}: {e}"
                )

        raise RuntimeError(
            f"[{self.name}] All {MAX_RETRIES} attempts failed. Last error: {last_error}"
        )
