"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Unit tests for Formula Engine.

Tests the formula validation, evaluation, and security features.
"""

import pytest
from app.services.formula_engine import FormulaEngine, FormulaResult, FormulaValidation


class TestFormulaValidation:
    """Test formula validation functionality."""

    def test_valid_simple_formula(self):
        """Test validating a simple valid formula."""
        result = FormulaEngine.validate("base_price * quantity")

        assert result.valid is True
        assert result.error is None
        assert "base_price" in result.variables_found
        assert "quantity" in result.variables_found

    def test_valid_complex_formula(self):
        """Test validating a complex formula with math functions."""
        result = FormulaEngine.validate(
            "max(base_price * sq_ft, 250) + ceil(stories / 2) * 100"
        )

        assert result.valid is True
        assert result.error is None
        assert "base_price" in result.variables_found
        assert "sq_ft" in result.variables_found
        assert "stories" in result.variables_found

    def test_invalid_syntax(self):
        """Test detecting syntax errors."""
        result = FormulaEngine.validate("base_price * sq_ft +")

        assert result.valid is False
        assert result.error is not None
        assert "syntax" in result.error.lower()

    def test_empty_formula(self):
        """Test handling empty formula."""
        result = FormulaEngine.validate("")

        assert result.valid is False
        assert "empty" in result.error.lower()

    def test_dangerous_import_blocked(self):
        """Test that import statements are blocked."""
        result = FormulaEngine.validate("import os")

        assert result.valid is False
        assert "forbidden" in result.error.lower()

    def test_dangerous_exec_blocked(self):
        """Test that exec calls are blocked."""
        result = FormulaEngine.validate("exec('malicious code')")

        assert result.valid is False
        assert "forbidden" in result.error.lower()

    def test_dunder_methods_blocked(self):
        """Test that dunder methods are blocked."""
        result = FormulaEngine.validate("__import__('os')")

        assert result.valid is False
        assert "forbidden" in result.error.lower()


class TestFormulaEvaluation:
    """Test formula evaluation functionality."""

    def test_simple_multiplication(self):
        """Test simple multiplication formula."""
        result = FormulaEngine.evaluate(
            "base_price * quantity",
            {"quantity": 10},
            base_price=5.0
        )

        assert result.success is True
        assert result.result == 50.0
        assert result.error is None
        assert "quantity" in result.variables_used

    def test_complex_calculation(self):
        """Test complex formula with multiple operations."""
        result = FormulaEngine.evaluate(
            "base_price * sq_ft + (stories - 1) * 50 + window_count * 8",
            {"sq_ft": 2500, "stories": 2, "window_count": 20},
            base_price=0.15
        )

        assert result.success is True
        # 0.15 * 2500 + (2-1) * 50 + 20 * 8 = 375 + 50 + 160 = 585
        assert result.result == 585.0

    def test_math_functions(self):
        """Test math functions (min, max, abs, round, etc.)."""
        result = FormulaEngine.evaluate(
            "max(100, 250) + min(50, 25) + abs(-10) + round(3.7)",
            {},
            base_price=None
        )

        assert result.success is True
        # max(100, 250) + min(50, 25) + abs(-10) + round(3.7)
        # = 250 + 25 + 10 + 4 = 289
        assert result.result == 289.0

    def test_conditional_expression(self):
        """Test ternary conditional expressions."""
        # Test true condition
        result1 = FormulaEngine.evaluate(
            "100 if sq_ft > 2000 else 50",
            {"sq_ft": 2500},
            base_price=None
        )
        assert result1.success is True
        assert result1.result == 100.0

        # Test false condition
        result2 = FormulaEngine.evaluate(
            "100 if sq_ft > 2000 else 50",
            {"sq_ft": 1500},
            base_price=None
        )
        assert result2.success is True
        assert result2.result == 50.0

    def test_missing_variable_error(self):
        """Test error when variable is missing."""
        result = FormulaEngine.evaluate(
            "base_price * sq_ft + stories * 50",
            {"sq_ft": 2500},  # Missing 'stories'
            base_price=0.15
        )

        assert result.success is False
        assert "stories" in result.error
        assert "not found" in result.error.lower()

    def test_division_by_zero(self):
        """Test division by zero error handling."""
        result = FormulaEngine.evaluate(
            "100 / (stories - stories)",
            {"stories": 2},
            base_price=None
        )

        assert result.success is False
        assert "division by zero" in result.error.lower()

    def test_invalid_result_nan(self):
        """Test handling of NaN results."""
        result = FormulaEngine.evaluate(
            "sqrt(-1)",
            {},
            base_price=None
        )

        assert result.success is False
        assert "invalid result" in result.error.lower()

    def test_type_conversion(self):
        """Test automatic type conversion of variables."""
        result = FormulaEngine.evaluate(
            "base_price * quantity",
            {"quantity": "10"},  # String instead of number
            base_price=5.0
        )

        assert result.success is True
        assert result.result == 50.0

    def test_ceil_and_floor(self):
        """Test ceil and floor functions."""
        result = FormulaEngine.evaluate(
            "ceil(3.2) + floor(3.8)",
            {},
            base_price=None
        )

        assert result.success is True
        # ceil(3.2) = 4, floor(3.8) = 3
        assert result.result == 7.0

    def test_sqrt_function(self):
        """Test square root function."""
        result = FormulaEngine.evaluate(
            "sqrt(16) + sqrt(25)",
            {},
            base_price=None
        )

        assert result.success is True
        assert result.result == 9.0  # 4 + 5

    def test_pow_function(self):
        """Test power function."""
        result = FormulaEngine.evaluate(
            "pow(2, 3) + pow(5, 2)",
            {},
            base_price=None
        )

        assert result.success is True
        assert result.result == 33.0  # 8 + 25

    def test_execution_time_tracking(self):
        """Test that execution time is tracked."""
        result = FormulaEngine.evaluate(
            "base_price * quantity",
            {"quantity": 10},
            base_price=5.0
        )

        assert result.execution_time_ms >= 0
        assert result.execution_time_ms < 1000  # Should be very fast


class TestFormulaTesting:
    """Test batch testing functionality."""

    def test_batch_testing(self):
        """Test running multiple test cases."""
        test_cases = [
            {"sq_ft": 1500},
            {"sq_ft": 2500},
            {"sq_ft": 4000},
        ]

        results = FormulaEngine.test_formula(
            "base_price * sq_ft",
            test_cases,
            base_price=0.15
        )

        assert len(results) == 3

        # Check each result
        for (test_case, result) in results:
            assert result.success is True
            assert result.result == 0.15 * test_case["sq_ft"]

    def test_batch_testing_with_errors(self):
        """Test batch testing with some failing cases."""
        test_cases = [
            {"sq_ft": 1500, "stories": 2},  # Valid
            {"sq_ft": 2500},  # Missing 'stories' - will fail
            {"sq_ft": 4000, "stories": 3},  # Valid
        ]

        results = FormulaEngine.test_formula(
            "base_price * sq_ft + (stories - 1) * 50",
            test_cases,
            base_price=0.15
        )

        assert len(results) == 3
        assert results[0][1].success is True  # First case passes
        assert results[1][1].success is False  # Second case fails
        assert results[2][1].success is True  # Third case passes


class TestExampleFormulas:
    """Test example formulas functionality."""

    def test_get_examples(self):
        """Test retrieving example formulas."""
        examples = FormulaEngine.get_example_formulas()

        assert len(examples) > 0

        # Check structure of first example
        first = examples[0]
        assert "name" in first
        assert "formula" in first
        assert "description" in first
        assert "variables" in first

    def test_all_examples_valid(self):
        """Test that all example formulas are valid."""
        examples = FormulaEngine.get_example_formulas()

        for example in examples:
            validation = FormulaEngine.validate(example["formula"])
            assert validation.valid is True, f"Example '{example['name']}' has invalid formula"


class TestSecurityFeatures:
    """Test security features of formula engine."""

    def test_no_file_access(self):
        """Test that file operations are blocked."""
        result = FormulaEngine.validate("open('/etc/passwd')")

        assert result.valid is False
        assert "forbidden" in result.error.lower()

    def test_no_system_calls(self):
        """Test that system calls are blocked."""
        result = FormulaEngine.validate("os.system('ls')")

        # Should fail during validation (syntax error or forbidden pattern)
        # or during evaluation (NameError for 'os')
        assert result.valid is False or "os" in str(result.error)

    def test_no_nested_eval(self):
        """Test that nested eval calls are blocked."""
        result = FormulaEngine.validate("eval('1 + 1')")

        assert result.valid is False
        assert "forbidden" in result.error.lower()

    def test_no_compile(self):
        """Test that compile calls are blocked."""
        result = FormulaEngine.validate("compile('1 + 1', '<string>', 'eval')")

        assert result.valid is False
        assert "forbidden" in result.error.lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_numbers(self):
        """Test handling of very large numbers."""
        result = FormulaEngine.evaluate(
            "quantity * 1000000",
            {"quantity": 999999},
            base_price=None
        )

        assert result.success is True
        assert result.result == 999999000000.0

    def test_very_small_numbers(self):
        """Test handling of very small numbers."""
        result = FormulaEngine.evaluate(
            "base_price * 0.0001",
            {},
            base_price=0.0001
        )

        assert result.success is True
        assert result.result < 0.001

    def test_zero_base_price(self):
        """Test handling of zero base price."""
        result = FormulaEngine.evaluate(
            "base_price * quantity",
            {"quantity": 100},
            base_price=0.0
        )

        assert result.success is True
        assert result.result == 0.0

    def test_negative_numbers(self):
        """Test handling of negative numbers."""
        result = FormulaEngine.evaluate(
            "base_price + discount",
            {"discount": -50},
            base_price=100
        )

        assert result.success is True
        assert result.result == 50.0

    def test_whitespace_in_formula(self):
        """Test that whitespace is handled correctly."""
        result = FormulaEngine.evaluate(
            "  base_price   *   quantity  ",
            {"quantity": 10},
            base_price=5.0
        )

        assert result.success is True
        assert result.result == 50.0

    def test_parentheses_precedence(self):
        """Test operator precedence with parentheses."""
        result = FormulaEngine.evaluate(
            "(2 + 3) * 4",
            {},
            base_price=None
        )

        assert result.success is True
        assert result.result == 20.0  # Not 14


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
