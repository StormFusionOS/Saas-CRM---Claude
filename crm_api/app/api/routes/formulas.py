"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Formula Testing & Validation Routes."""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.api.deps import require_sales_claims
from app.services.formula_engine import FormulaEngine


router = APIRouter(tags=["formulas"])


# ============================================================================
# Request/Response Models
# ============================================================================


class ValidateFormulaRequest(BaseModel):
    """Request to validate a formula."""
    formula: str = Field(..., description="Formula to validate")


class ValidateFormulaResponse(BaseModel):
    """Response from formula validation."""
    valid: bool
    error: Optional[str] = None
    variables_found: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None


class EvaluateFormulaRequest(BaseModel):
    """Request to evaluate a formula."""
    formula: str = Field(..., description="Formula to evaluate")
    variables: Dict[str, Any] = Field(..., description="Variable values")
    base_price: Optional[float] = Field(None, description="Optional base price")


class EvaluateFormulaResponse(BaseModel):
    """Response from formula evaluation."""
    success: bool
    result: Optional[float] = None
    error: Optional[str] = None
    variables_used: Optional[List[str]] = None
    execution_time_ms: float


class TestCase(BaseModel):
    """Test case for formula testing."""
    name: str = Field(..., description="Test case name")
    variables: Dict[str, Any] = Field(..., description="Variable values")
    expected_result: Optional[float] = Field(None, description="Expected result (optional)")


class TestFormulaRequest(BaseModel):
    """Request to test a formula with multiple test cases."""
    formula: str = Field(..., description="Formula to test")
    test_cases: List[TestCase] = Field(..., description="Test cases to run")
    base_price: Optional[float] = Field(None, description="Optional base price")


class TestFormulaResult(BaseModel):
    """Result of a single test case."""
    test_case_name: str
    variables: Dict[str, Any]
    expected_result: Optional[float]
    actual_result: Optional[float]
    success: bool
    error: Optional[str] = None
    passed: Optional[bool] = None  # True if matches expected, False if not, None if no expected
    execution_time_ms: float


class TestFormulaResponse(BaseModel):
    """Response from formula testing."""
    total_tests: int
    passed: int
    failed: int
    errors: int
    results: List[TestFormulaResult]


class ExampleFormula(BaseModel):
    """Example formula with description."""
    name: str
    formula: str
    description: str
    variables: List[str]


class ExampleFormulasResponse(BaseModel):
    """Response with example formulas."""
    examples: List[ExampleFormula]


# ============================================================================
# Routes
# ============================================================================


@router.post("/formulas/validate", response_model=ValidateFormulaResponse)
def validate_formula(
    request: ValidateFormulaRequest,
    current_user: dict = Depends(require_sales_claims),
) -> ValidateFormulaResponse:
    """
    Validate a pricing formula for syntax and security.

    This endpoint checks if a formula is syntactically correct and safe to execute.
    It also identifies variables used in the formula.

    **STAFF ONLY**
    """
    validation = FormulaEngine.validate(request.formula)

    return ValidateFormulaResponse(
        valid=validation.valid,
        error=validation.error,
        variables_found=validation.variables_found,
        suggestions=validation.suggestions
    )


@router.post("/formulas/evaluate", response_model=EvaluateFormulaResponse)
def evaluate_formula(
    request: EvaluateFormulaRequest,
    current_user: dict = Depends(require_sales_claims),
) -> EvaluateFormulaResponse:
    """
    Evaluate a pricing formula with provided variables.

    This endpoint executes the formula with the given variable values
    and returns the calculated result.

    **STAFF ONLY**
    """
    result = FormulaEngine.evaluate(
        formula=request.formula,
        variables=request.variables,
        base_price=request.base_price
    )

    return EvaluateFormulaResponse(
        success=result.success,
        result=result.result,
        error=result.error,
        variables_used=result.variables_used,
        execution_time_ms=result.execution_time_ms
    )


@router.post("/formulas/test", response_model=TestFormulaResponse)
def test_formula(
    request: TestFormulaRequest,
    current_user: dict = Depends(require_sales_claims),
) -> TestFormulaResponse:
    """
    Test a formula with multiple test cases.

    This endpoint runs the formula against multiple test cases and reports
    which tests passed, failed, or had errors.

    **STAFF ONLY**
    """
    results = []
    passed = 0
    failed = 0
    errors = 0

    for test_case in request.test_cases:
        result = FormulaEngine.evaluate(
            formula=request.formula,
            variables=test_case.variables,
            base_price=request.base_price
        )

        # Determine if test passed
        test_passed = None
        if test_case.expected_result is not None and result.success:
            # Allow for small floating point differences
            diff = abs(result.result - test_case.expected_result)
            test_passed = diff < 0.01

            if test_passed:
                passed += 1
            else:
                failed += 1
        elif not result.success:
            errors += 1

        results.append(TestFormulaResult(
            test_case_name=test_case.name,
            variables=test_case.variables,
            expected_result=test_case.expected_result,
            actual_result=result.result,
            success=result.success,
            error=result.error,
            passed=test_passed,
            execution_time_ms=result.execution_time_ms
        ))

    return TestFormulaResponse(
        total_tests=len(request.test_cases),
        passed=passed,
        failed=failed,
        errors=errors,
        results=results
    )


@router.get("/formulas/examples", response_model=ExampleFormulasResponse)
def get_example_formulas(
    current_user: dict = Depends(require_sales_claims),
) -> ExampleFormulasResponse:
    """
    Get example formulas for common pricing scenarios.

    Returns a list of example formulas with descriptions and required variables.

    **STAFF ONLY**
    """
    examples = FormulaEngine.get_example_formulas()

    return ExampleFormulasResponse(
        examples=[
            ExampleFormula(
                name=ex["name"],
                formula=ex["formula"],
                description=ex["description"],
                variables=ex["variables"]
            )
            for ex in examples
        ]
    )


__all__ = ["router"]
