"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Formula Engine Service - Advanced pricing formula evaluation.

Provides safe formula evaluation with comprehensive math functions,
validation, and error handling.
"""

import re
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FormulaResult:
    """Result of formula evaluation."""
    success: bool
    result: Optional[float] = None
    error: Optional[str] = None
    variables_used: List[str] = None
    execution_time_ms: float = 0.0


@dataclass
class FormulaValidation:
    """Result of formula validation."""
    valid: bool
    error: Optional[str] = None
    variables_found: List[str] = None
    suggestions: List[str] = None


class FormulaEngine:
    """
    Safe formula evaluation engine for pricing calculations.

    Supports:
    - Basic arithmetic: +, -, *, /, **, %, //
    - Comparison: <, >, <=, >=, ==, !=
    - Logical: and, or, not
    - Math functions: min, max, abs, round, ceil, floor, sqrt, pow
    - Conditional: if/else using ternary operator
    """

    # Allowed math functions
    SAFE_FUNCTIONS = {
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
        'ceil': math.ceil,
        'floor': math.floor,
        'sqrt': math.sqrt,
        'pow': pow,
    }

    # Common variable patterns
    COMMON_VARIABLES = [
        'base_price', 'sq_ft', 'linear_ft', 'stories', 'window_count',
        'pitch_difficulty', 'height', 'quantity', 'hours', 'difficulty',
        'area', 'perimeter', 'volume', 'distance', 'weight'
    ]

    @classmethod
    def evaluate(
        cls,
        formula: str,
        variables: Dict[str, Any],
        base_price: Optional[float] = None
    ) -> FormulaResult:
        """
        Safely evaluate a pricing formula.

        Args:
            formula: Formula string to evaluate
            variables: Variable values to use in the formula
            base_price: Optional base price to include in namespace

        Returns:
            FormulaResult with success status and result or error
        """
        import time
        start_time = time.time()

        try:
            # Validate formula first
            validation = cls.validate(formula)
            if not validation.valid:
                return FormulaResult(
                    success=False,
                    error=validation.error,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            # Build safe namespace
            namespace = {
                '__builtins__': {},
                **cls.SAFE_FUNCTIONS,
            }

            # Add base_price if provided
            if base_price is not None:
                namespace['base_price'] = float(base_price)

            # Add variables, converting to float where possible
            variables_used = []
            for key, value in variables.items():
                try:
                    namespace[key] = float(value)
                    variables_used.append(key)
                except (ValueError, TypeError):
                    namespace[key] = value
                    variables_used.append(key)

            # Evaluate formula
            result = eval(formula, namespace, {})

            # Convert result to float
            try:
                result_float = float(result)
            except (ValueError, TypeError):
                return FormulaResult(
                    success=False,
                    error=f"Formula result '{result}' cannot be converted to a number",
                    variables_used=variables_used,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            # Check for invalid results
            if math.isnan(result_float) or math.isinf(result_float):
                return FormulaResult(
                    success=False,
                    error=f"Formula produced invalid result: {result_float}",
                    variables_used=variables_used,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            execution_time = (time.time() - start_time) * 1000

            return FormulaResult(
                success=True,
                result=round(result_float, 2),
                variables_used=variables_used,
                execution_time_ms=execution_time
            )

        except ZeroDivisionError:
            return FormulaResult(
                success=False,
                error="Division by zero in formula",
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except NameError as e:
            missing_var = str(e).split("'")[1] if "'" in str(e) else "unknown"
            return FormulaResult(
                success=False,
                error=f"Variable '{missing_var}' not found. Available: {', '.join(variables.keys())}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except SyntaxError as e:
            return FormulaResult(
                success=False,
                error=f"Syntax error in formula: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return FormulaResult(
                success=False,
                error=f"Error evaluating formula: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )

    @classmethod
    def validate(cls, formula: str) -> FormulaValidation:
        """
        Validate a formula for syntax and security.

        Args:
            formula: Formula string to validate

        Returns:
            FormulaValidation with validation results
        """
        if not formula or not formula.strip():
            return FormulaValidation(
                valid=False,
                error="Formula cannot be empty"
            )

        # Check for dangerous patterns
        dangerous_patterns = [
            r'__\w+__',  # Dunder methods
            r'import\s',  # Import statements
            r'exec\s*\(',  # exec calls
            r'eval\s*\(',  # eval calls (nested)
            r'compile\s*\(',  # compile calls
            r'open\s*\(',  # file operations
            r'\.system\(',  # system calls
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, formula):
                return FormulaValidation(
                    valid=False,
                    error=f"Formula contains forbidden pattern: {pattern}"
                )

        # Extract variable names (simple alphanumeric identifiers)
        variable_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        all_identifiers = re.findall(variable_pattern, formula)

        # Filter out function names and Python keywords
        python_keywords = {'if', 'else', 'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None'}
        variables_found = [
            var for var in set(all_identifiers)
            if var not in cls.SAFE_FUNCTIONS
            and var not in python_keywords
        ]

        # Test syntax by attempting to compile
        try:
            compile(formula, '<formula>', 'eval')
        except SyntaxError as e:
            return FormulaValidation(
                valid=False,
                error=f"Syntax error: {str(e)}",
                variables_found=variables_found
            )

        # Generate suggestions for common variables
        suggestions = []
        for var in variables_found:
            if var not in cls.COMMON_VARIABLES:
                # Find similar common variables
                similar = [
                    common_var for common_var in cls.COMMON_VARIABLES
                    if common_var.startswith(var[:2]) or var.startswith(common_var[:2])
                ]
                if similar:
                    suggestions.append(f"Did you mean: {', '.join(similar[:3])}?")

        return FormulaValidation(
            valid=True,
            variables_found=variables_found,
            suggestions=suggestions if suggestions else None
        )

    @classmethod
    def test_formula(
        cls,
        formula: str,
        test_cases: List[Dict[str, Any]],
        base_price: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], FormulaResult]]:
        """
        Test a formula with multiple test cases.

        Args:
            formula: Formula to test
            test_cases: List of variable dictionaries to test
            base_price: Optional base price

        Returns:
            List of (test_case, result) tuples
        """
        results = []
        for test_case in test_cases:
            result = cls.evaluate(formula, test_case, base_price)
            results.append((test_case, result))
        return results

    @classmethod
    def get_example_formulas(cls) -> List[Dict[str, str]]:
        """
        Get example formulas for common scenarios.

        Returns:
            List of example formulas with descriptions
        """
        return [
            {
                "name": "Simple per-unit pricing",
                "formula": "base_price * quantity",
                "description": "Multiply base price by quantity",
                "variables": ["base_price", "quantity"]
            },
            {
                "name": "Area-based pricing",
                "formula": "base_price * sq_ft",
                "description": "Price based on square footage",
                "variables": ["base_price", "sq_ft"]
            },
            {
                "name": "Multi-story adjustment",
                "formula": "base_price * sq_ft + (stories - 1) * 50",
                "description": "Base price plus $50 per additional story",
                "variables": ["base_price", "sq_ft", "stories"]
            },
            {
                "name": "Difficulty multiplier",
                "formula": "base_price * sq_ft * difficulty",
                "description": "Base price multiplied by difficulty factor",
                "variables": ["base_price", "sq_ft", "difficulty"]
            },
            {
                "name": "Minimum price guarantee",
                "formula": "max(base_price * quantity, 100)",
                "description": "Ensure minimum $100 charge",
                "variables": ["base_price", "quantity"]
            },
            {
                "name": "Volume discount",
                "formula": "base_price * sq_ft * (0.9 if sq_ft > 5000 else 1.0)",
                "description": "10% discount for areas over 5000 sq ft",
                "variables": ["base_price", "sq_ft"]
            },
            {
                "name": "Tiered pricing",
                "formula": "base_price * (100 + (max(sq_ft - 1000, 0) * 0.8))",
                "description": "Full price for first 1000 sq ft, 80% after",
                "variables": ["base_price", "sq_ft"]
            },
            {
                "name": "Complex calculation",
                "formula": "base_price * sq_ft * (1 + stories * 0.15) + (window_count * 8)",
                "description": "Base + 15% per story + $8 per window",
                "variables": ["base_price", "sq_ft", "stories", "window_count"]
            },
        ]


__all__ = ["FormulaEngine", "FormulaResult", "FormulaValidation"]
