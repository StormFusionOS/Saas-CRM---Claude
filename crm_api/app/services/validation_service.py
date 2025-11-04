"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Validation Service with Auto-Retry

Validates AI-generated outputs against JSON schemas and rules.
Implements self-healing retry logic for malformed outputs.
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import re
import structlog
from jsonschema import validate, ValidationError as JSONSchemaValidationError

from app.models.prompt_template import (
    ValidationRule,
    OutputType,
    get_output_schema,
    get_validation_rules
)

logger = structlog.get_logger(__name__)


class ValidationService:
    """
    Service for validating AI-generated outputs.

    Supports JSON schema validation and custom rules.
    """

    def __init__(self):
        self.logger = logger.bind(service="validation")

    # ==========================================================================
    # Schema Validation
    # ==========================================================================

    def validate_against_schema(
        self,
        output: Dict[str, Any],
        output_type: OutputType
    ) -> Tuple[bool, List[str]]:
        """
        Validate output against JSON schema.

        Args:
            output: Generated output (parsed JSON)
            output_type: Type of output

        Returns:
            Tuple of (is_valid, errors)
        """
        schema = get_output_schema(output_type)
        errors = []

        try:
            validate(instance=output, schema=schema)
            self.logger.debug("schema_validation_passed", output_type=output_type)
            return True, []

        except JSONSchemaValidationError as e:
            error_msg = f"Schema validation failed: {e.message}"
            errors.append(error_msg)
            self.logger.warning(
                "schema_validation_failed",
                output_type=output_type,
                error=error_msg
            )
            return False, errors

        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            errors.append(error_msg)
            return False, errors

    # ==========================================================================
    # Rule-Based Validation
    # ==========================================================================

    def validate_rules(
        self,
        output: Dict[str, Any],
        rules: List[ValidationRule]
    ) -> Tuple[bool, List[str]]:
        """
        Validate output against custom rules.

        Args:
            output: Generated output
            rules: List of validation rules

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        for rule in rules:
            try:
                value = self._get_field_value(output, rule.field_path)

                if rule.rule_type == "length":
                    if not self._validate_length(value, rule.constraint):
                        errors.append(rule.error_message)

                elif rule.rule_type == "range":
                    if not self._validate_range(value, rule.constraint):
                        errors.append(rule.error_message)

                elif rule.rule_type == "format":
                    if not self._validate_format(value, rule.constraint):
                        errors.append(rule.error_message)

                elif rule.rule_type == "required_field":
                    if not self._validate_required(output, rule.constraint):
                        errors.append(rule.error_message)

                elif rule.rule_type == "array_length":
                    if not self._validate_array_length(value, rule.constraint):
                        errors.append(rule.error_message)

            except Exception as e:
                errors.append(f"Rule '{rule.rule_id}' validation failed: {str(e)}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def _get_field_value(self, output: Dict[str, Any], field_path: str) -> Any:
        """
        Get value from output using JSON path.

        Supports:
        - Simple: "meta_title"
        - Nested: "faqs.0.question"
        - Wildcard: "faqs[*].question" (returns list)
        """
        # Handle wildcard paths
        if "[*]" in field_path:
            return self._get_wildcard_values(output, field_path)

        # Handle dot notation
        parts = field_path.split(".")
        value = output

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list) and part.isdigit():
                value = value[int(part)]
            else:
                return None

        return value

    def _get_wildcard_values(self, output: Dict[str, Any], field_path: str) -> List[Any]:
        """Get all values matching wildcard path."""
        # e.g., "faqs[*].question" -> get all questions from faqs array
        parts = field_path.split("[*]")
        array_path = parts[0]
        field_name = parts[1].lstrip(".")

        array = self._get_field_value(output, array_path)
        if not isinstance(array, list):
            return []

        return [item.get(field_name) for item in array if isinstance(item, dict)]

    # ==========================================================================
    # Specific Validators
    # ==========================================================================

    def _validate_length(self, value: Any, constraint: Dict[str, int]) -> bool:
        """Validate string length."""
        if not isinstance(value, str):
            return False

        length = len(value)
        min_len = constraint.get("min", 0)
        max_len = constraint.get("max", float("inf"))

        return min_len <= length <= max_len

    def _validate_range(self, value: Any, constraint: Dict[str, float]) -> bool:
        """Validate numeric range."""
        if not isinstance(value, (int, float)):
            return False

        min_val = constraint.get("min", float("-inf"))
        max_val = constraint.get("max", float("inf"))

        return min_val <= value <= max_val

    def _validate_format(self, value: Any, constraint: Dict[str, str]) -> bool:
        """Validate format (e.g., URI, email)."""
        if not isinstance(value, str):
            return False

        format_type = constraint.get("format")

        if format_type == "uri":
            # Basic URL validation
            url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
            return bool(re.match(url_pattern, value))

        elif format_type == "email":
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            return bool(re.match(email_pattern, value))

        return True

    def _validate_required(self, output: Dict[str, Any], constraint: Dict[str, Any]) -> bool:
        """Validate required field presence."""
        field = constraint.get("field")
        if field and field not in output:
            return False

        # Check if keyword appears in another field
        must_appear_in = constraint.get("must_appear_in")
        if must_appear_in:
            target_field = output.get(must_appear_in, "")
            search_value = output.get(constraint.get("field", ""), "")
            if search_value and search_value.lower() not in target_field.lower():
                return False

        return True

    def _validate_array_length(self, value: Any, constraint: Dict[str, int]) -> bool:
        """Validate array length."""
        if not isinstance(value, list):
            return False

        length = len(value)
        min_len = constraint.get("min", 0)
        max_len = constraint.get("max", float("inf"))

        return min_len <= length <= max_len

    # ==========================================================================
    # Combined Validation
    # ==========================================================================

    def validate_output(
        self,
        raw_output: str,
        output_type: OutputType,
        custom_rules: Optional[List[ValidationRule]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Comprehensive validation: parse JSON + schema + rules.

        Args:
            raw_output: Raw LLM output (string)
            output_type: Expected output type
            custom_rules: Additional custom rules

        Returns:
            Tuple of (is_valid, parsed_output, errors)
        """
        errors = []

        # Step 1: Parse JSON
        try:
            parsed_output = json.loads(raw_output)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")
            return False, None, errors

        # Step 2: Schema validation
        schema_valid, schema_errors = self.validate_against_schema(
            parsed_output,
            output_type
        )
        errors.extend(schema_errors)

        # Step 3: Rule validation
        rules = get_validation_rules(output_type)
        if custom_rules:
            rules.extend(custom_rules)

        rules_valid, rule_errors = self.validate_rules(parsed_output, rules)
        errors.extend(rule_errors)

        # Overall validation
        is_valid = schema_valid and rules_valid

        return is_valid, parsed_output, errors

    # ==========================================================================
    # Retry Prompt Generation
    # ==========================================================================

    def generate_retry_prompt(
        self,
        original_prompt: str,
        failed_output: str,
        errors: List[str],
        attempt_number: int
    ) -> str:
        """
        Generate retry prompt with error feedback.

        Args:
            original_prompt: Original prompt
            failed_output: Failed output
            errors: Validation errors
            attempt_number: Current retry attempt

        Returns:
            Retry prompt with corrections
        """
        error_summary = "\n".join(f"- {error}" for error in errors)

        retry_prompt = f"""
{original_prompt}

---

⚠️ RETRY ATTEMPT #{attempt_number}

Your previous output had the following validation errors:
{error_summary}

Previous output:
{failed_output[:500]}...

Please fix these errors and regenerate the output. Ensure:
1. Valid JSON format
2. All required fields present
3. Values within specified constraints
4. Proper data types

Generate corrected output:
"""
        return retry_prompt

    # ==========================================================================
    # Auto-Retry Logic
    # ==========================================================================

    def validate_with_retry(
        self,
        generate_func,
        prompt: str,
        output_type: OutputType,
        max_retries: int = 3
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str], int]:
        """
        Validate output with automatic retry on failure.

        Args:
            generate_func: Function that generates output (callable)
            prompt: Initial prompt
            output_type: Expected output type
            max_retries: Maximum retry attempts

        Returns:
            Tuple of (success, parsed_output, errors, attempts_used)
        """
        current_prompt = prompt
        attempts = 0

        while attempts < max_retries:
            attempts += 1

            # Generate output
            raw_output = generate_func(current_prompt)

            # Validate
            is_valid, parsed_output, errors = self.validate_output(
                raw_output,
                output_type
            )

            if is_valid:
                self.logger.info(
                    "validation_success",
                    attempts=attempts,
                    output_type=output_type
                )
                return True, parsed_output, [], attempts

            # Generate retry prompt
            if attempts < max_retries:
                current_prompt = self.generate_retry_prompt(
                    prompt,
                    raw_output,
                    errors,
                    attempts + 1
                )
                self.logger.warning(
                    "validation_failed_retrying",
                    attempt=attempts,
                    errors=errors
                )

        # All retries exhausted
        self.logger.error(
            "validation_failed_max_retries",
            attempts=attempts,
            final_errors=errors
        )
        return False, None, errors, attempts


# ==============================================================================
# Singleton Instance
# ==============================================================================

_validation_service: Optional[ValidationService] = None


def get_validation_service() -> ValidationService:
    """Get or create validation service instance."""
    global _validation_service

    if _validation_service is None:
        _validation_service = ValidationService()

    return _validation_service
