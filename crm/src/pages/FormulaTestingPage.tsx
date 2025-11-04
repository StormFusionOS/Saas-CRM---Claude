/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { useAuth } from '../lib/auth-context';

interface FormulaValidation {
  valid: boolean;
  error?: string;
  variables_found?: string[];
  suggestions?: string[];
}

interface FormulaResult {
  success: boolean;
  result?: number;
  error?: string;
  variables_used?: string[];
  execution_time_ms: number;
}

interface ExampleFormula {
  name: string;
  formula: string;
  description: string;
  variables: string[];
}

interface TestCase {
  name: string;
  variables: Record<string, number>;
  expected_result?: number;
}

interface TestResult {
  test_case_name: string;
  variables: Record<string, number>;
  expected_result?: number;
  actual_result?: number;
  success: boolean;
  error?: string;
  passed?: boolean;
  execution_time_ms: number;
}

const FormulaTestingPage: React.FC = () => {
  const { token } = useAuth();
  const [formula, setFormula] = useState('base_price * sq_ft');
  const [basePrice, setBasePrice] = useState('0.15');
  const [variables, setVariables] = useState<Record<string, string>>({
    sq_ft: '2500',
    stories: '2',
    linear_ft: '150',
    window_count: '20',
  });
  const [validation, setValidation] = useState<FormulaValidation | null>(null);
  const [result, setResult] = useState<FormulaResult | null>(null);
  const [examples, setExamples] = useState<ExampleFormula[]>([]);
  const [testCases, setTestCases] = useState<TestCase[]>([
    { name: 'Small house', variables: { sq_ft: 1500, stories: 1 } },
    { name: 'Medium house', variables: { sq_ft: 2500, stories: 2 } },
    { name: 'Large house', variables: { sq_ft: 4000, stories: 2 } },
  ]);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'single' | 'batch' | 'examples'>('single');

  // Load examples on mount
  useEffect(() => {
    const fetchExamples = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/formulas/examples', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setExamples(data.examples);
        }
      } catch (err) {
        console.error('Error loading examples:', err);
      }
    };
    fetchExamples();
  }, [token]);

  // Auto-validate formula
  useEffect(() => {
    const validateFormula = async () => {
      if (!formula.trim()) {
        setValidation(null);
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/v1/formulas/validate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ formula }),
        });

        const data = await response.json();
        setValidation(data);
      } catch (err) {
        console.error('Validation error:', err);
      }
    };

    const debounce = setTimeout(validateFormula, 300);
    return () => clearTimeout(debounce);
  }, [formula, token]);

  // Evaluate formula
  const evaluateFormula = async () => {
    setLoading(true);
    setError('');

    try {
      // Convert string variables to numbers
      const numericVars: Record<string, number> = {};
      for (const [key, value] of Object.entries(variables)) {
        numericVars[key] = parseFloat(value) || 0;
      }

      const response = await fetch('http://localhost:8000/api/v1/formulas/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          formula,
          variables: numericVars,
          base_price: basePrice ? parseFloat(basePrice) : null,
        }),
      });

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Evaluation failed');
    } finally {
      setLoading(false);
    }
  };

  // Test formula with multiple test cases
  const runBatchTests = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/formulas/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          formula,
          test_cases: testCases,
          base_price: basePrice ? parseFloat(basePrice) : null,
        }),
      });

      const data = await response.json();
      setTestResults(data.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Testing failed');
    } finally {
      setLoading(false);
    }
  };

  // Add variable
  const addVariable = () => {
    const newVarName = prompt('Enter variable name:');
    if (newVarName && !variables[newVarName]) {
      setVariables({ ...variables, [newVarName]: '0' });
    }
  };

  // Remove variable
  const removeVariable = (key: string) => {
    const { [key]: _, ...rest } = variables;
    setVariables(rest);
  };

  // Load example formula
  const loadExample = (example: ExampleFormula) => {
    setFormula(example.formula);
    const newVars: Record<string, string> = {};
    example.variables.forEach((v) => {
      if (v === 'base_price') return; // Skip base_price
      if (variables[v]) {
        newVars[v] = variables[v];
      } else {
        newVars[v] = '100';
      }
    });
    setVariables(newVars);
    setActiveTab('single');
  };

  // Add test case
  const addTestCase = () => {
    const name = prompt('Enter test case name:');
    if (name) {
      const numericVars: Record<string, number> = {};
      for (const [key, value] of Object.entries(variables)) {
        numericVars[key] = parseFloat(value) || 0;
      }
      setTestCases([...testCases, { name, variables: numericVars }]);
    }
  };

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <div>
          <h1 className="text-3xl font-display font-bold text-gradient">
            Formula Testing Lab
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Test and validate pricing formulas with interactive tools
          </p>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-8">
        {error && (
          <div className="mb-6 p-4 bg-error/10 border border-error rounded-base text-error">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Formula Editor */}
          <div className="lg:col-span-2 space-y-6">
            {/* Formula Input */}
            <Card animate="slide-in-up">
              <h2 className="text-xl font-display font-semibold mb-4">Formula</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Formula Expression
                  </label>
                  <textarea
                    value={formula}
                    onChange={(e) => setFormula(e.target.value)}
                    className="w-full px-4 py-3 bg-bg-elev text-text-primary border border-border-default rounded-base font-mono text-sm transition-all duration-base placeholder:text-text-muted focus-ring hover:border-border-strong min-h-[100px]"
                    placeholder="Enter your formula (e.g., base_price * sq_ft)"
                  />
                </div>

                {/* Validation Status */}
                {validation && (
                  <div
                    className={`p-3 rounded-base border ${
                      validation.valid
                        ? 'bg-success/10 border-success/30 text-success'
                        : 'bg-error/10 border-error/30 text-error'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-lg">{validation.valid ? '✓' : '✗'}</span>
                      <div className="flex-1">
                        {validation.valid ? (
                          <>
                            <p className="font-medium">Formula is valid</p>
                            {validation.variables_found && validation.variables_found.length > 0 && (
                              <p className="text-sm mt-1">
                                Variables: {validation.variables_found.join(', ')}
                              </p>
                            )}
                          </>
                        ) : (
                          <>
                            <p className="font-medium">Formula has errors</p>
                            {validation.error && <p className="text-sm mt-1">{validation.error}</p>}
                          </>
                        )}
                        {validation.suggestions && validation.suggestions.length > 0 && (
                          <div className="mt-2 text-sm">
                            {validation.suggestions.map((s, i) => (
                              <p key={i} className="text-text-muted">
                                {s}
                              </p>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <Input
                  id="base_price"
                  label="Base Price"
                  type="number"
                  step="0.01"
                  value={basePrice}
                  onChange={(e) => setBasePrice(e.target.value)}
                  placeholder="0.15"
                  helperText="Base price per unit"
                />
              </div>
            </Card>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-white/10">
              <button
                onClick={() => setActiveTab('single')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'single'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-text-muted hover:text-text-secondary'
                }`}
              >
                Single Test
              </button>
              <button
                onClick={() => setActiveTab('batch')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'batch'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-text-muted hover:text-text-secondary'
                }`}
              >
                Batch Testing
              </button>
              <button
                onClick={() => setActiveTab('examples')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'examples'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-text-muted hover:text-text-secondary'
                }`}
              >
                Examples
              </button>
            </div>

            {/* Single Test Tab */}
            {activeTab === 'single' && (
              <Card animate="fade-in">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-display font-semibold">Test Variables</h2>
                  <Button size="sm" variant="outline" onClick={addVariable}>
                    + Add Variable
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  {Object.entries(variables).map(([key, value]) => (
                    <div key={key} className="flex gap-2">
                      <Input
                        id={key}
                        label={key}
                        type="number"
                        step="any"
                        value={value}
                        onChange={(e) => setVariables({ ...variables, [key]: e.target.value })}
                        className="flex-1"
                      />
                      <button
                        onClick={() => removeVariable(key)}
                        className="mt-7 px-3 text-error hover:bg-error/10 rounded-base transition-colors"
                        title="Remove variable"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>

                <Button
                  onClick={evaluateFormula}
                  disabled={loading || !validation?.valid}
                  className="w-full"
                >
                  {loading ? 'Evaluating...' : 'Evaluate Formula'}
                </Button>

                {/* Result */}
                {result && (
                  <div className="mt-6">
                    {result.success ? (
                      <div className="p-4 bg-success/10 border border-success/30 rounded-base">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-text-muted">Result</p>
                            <p className="text-3xl font-bold text-success">
                              ${result.result?.toFixed(2)}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-text-muted">Execution Time</p>
                            <p className="text-sm font-mono text-text-secondary">
                              {result.execution_time_ms.toFixed(2)}ms
                            </p>
                          </div>
                        </div>
                        {result.variables_used && result.variables_used.length > 0 && (
                          <p className="text-xs text-text-muted mt-2">
                            Variables used: {result.variables_used.join(', ')}
                          </p>
                        )}
                      </div>
                    ) : (
                      <div className="p-4 bg-error/10 border border-error/30 rounded-base text-error">
                        <p className="font-medium">Evaluation Failed</p>
                        <p className="text-sm mt-1">{result.error}</p>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            )}

            {/* Batch Testing Tab */}
            {activeTab === 'batch' && (
              <Card animate="fade-in">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-display font-semibold">Test Cases</h2>
                  <Button size="sm" variant="outline" onClick={addTestCase}>
                    + Add Test Case
                  </Button>
                </div>

                <div className="space-y-4 mb-6">
                  {testCases.map((tc, i) => (
                    <div
                      key={i}
                      className="p-3 bg-bg-hover border border-border-default rounded-base"
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{tc.name}</p>
                          <p className="text-sm text-text-muted mt-1">
                            {Object.entries(tc.variables)
                              .map(([k, v]) => `${k}=${v}`)
                              .join(', ')}
                          </p>
                        </div>
                        <button
                          onClick={() => setTestCases(testCases.filter((_, idx) => idx !== i))}
                          className="text-error hover:bg-error/10 px-2 py-1 rounded-base"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                <Button
                  onClick={runBatchTests}
                  disabled={loading || !validation?.valid || testCases.length === 0}
                  className="w-full mb-6"
                >
                  {loading ? 'Running Tests...' : 'Run All Tests'}
                </Button>

                {/* Batch Test Results */}
                {testResults.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-medium text-text-primary">Results</h3>
                    {testResults.map((tr, i) => (
                      <div
                        key={i}
                        className={`p-3 border rounded-base ${
                          tr.success
                            ? 'bg-success/5 border-success/30'
                            : 'bg-error/5 border-error/30'
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-medium text-text-primary">{tr.test_case_name}</p>
                            <p className="text-sm text-text-muted mt-1">
                              {Object.entries(tr.variables)
                                .map(([k, v]) => `${k}=${v}`)
                                .join(', ')}
                            </p>
                          </div>
                          <div className="text-right">
                            {tr.success ? (
                              <>
                                <p className="text-lg font-bold text-success">
                                  ${tr.actual_result?.toFixed(2)}
                                </p>
                                <p className="text-xs text-text-muted">
                                  {tr.execution_time_ms.toFixed(1)}ms
                                </p>
                              </>
                            ) : (
                              <p className="text-sm text-error">{tr.error}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            )}

            {/* Examples Tab */}
            {activeTab === 'examples' && (
              <div className="space-y-4">
                {examples.map((example, i) => (
                  <Card key={i} animate="scale-in" className="glow-hover cursor-pointer" onClick={() => loadExample(example)}>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-lg font-display font-semibold text-gradient">
                          {example.name}
                        </h3>
                        <p className="text-sm text-text-muted mt-1">{example.description}</p>
                        <div className="mt-3 p-3 bg-bg-hover rounded-base">
                          <code className="text-sm text-accent">{example.formula}</code>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {example.variables.map((v) => (
                            <span
                              key={v}
                              className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full"
                            >
                              {v}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Right Column - Quick Reference */}
          <div className="space-y-6">
            <Card animate="slide-in-up">
              <h3 className="text-lg font-display font-semibold mb-4">Quick Reference</h3>

              <div className="space-y-4 text-sm">
                <div>
                  <h4 className="font-medium text-text-primary mb-2">Operators</h4>
                  <ul className="space-y-1 text-text-muted">
                    <li>
                      <code className="text-accent">+</code> Addition
                    </li>
                    <li>
                      <code className="text-accent">-</code> Subtraction
                    </li>
                    <li>
                      <code className="text-accent">*</code> Multiplication
                    </li>
                    <li>
                      <code className="text-accent">/</code> Division
                    </li>
                    <li>
                      <code className="text-accent">**</code> Exponentiation
                    </li>
                    <li>
                      <code className="text-accent">%</code> Modulo
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-medium text-text-primary mb-2">Functions</h4>
                  <ul className="space-y-1 text-text-muted">
                    <li>
                      <code className="text-accent">min(a, b)</code> Minimum
                    </li>
                    <li>
                      <code className="text-accent">max(a, b)</code> Maximum
                    </li>
                    <li>
                      <code className="text-accent">abs(x)</code> Absolute value
                    </li>
                    <li>
                      <code className="text-accent">round(x)</code> Round
                    </li>
                    <li>
                      <code className="text-accent">ceil(x)</code> Ceiling
                    </li>
                    <li>
                      <code className="text-accent">floor(x)</code> Floor
                    </li>
                    <li>
                      <code className="text-accent">sqrt(x)</code> Square root
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-medium text-text-primary mb-2">Conditionals</h4>
                  <ul className="space-y-1 text-text-muted">
                    <li>
                      <code className="text-accent">x if condition else y</code>
                    </li>
                    <li>
                      <code className="text-accent">{'<, >, <=, >=, ==, !='}</code>
                    </li>
                    <li>
                      <code className="text-accent">and, or, not</code>
                    </li>
                  </ul>
                </div>
              </div>
            </Card>

            <Card animate="slide-in-up">
              <h3 className="text-lg font-display font-semibold mb-4">Common Variables</h3>
              <div className="flex flex-wrap gap-2">
                {[
                  'base_price',
                  'sq_ft',
                  'linear_ft',
                  'stories',
                  'window_count',
                  'pitch_difficulty',
                  'quantity',
                  'hours',
                  'difficulty',
                ].map((v) => (
                  <button
                    key={v}
                    onClick={() => {
                      if (!variables[v]) {
                        setVariables({ ...variables, [v]: '100' });
                      }
                    }}
                    className="px-3 py-1.5 bg-bg-hover hover:bg-bg-elev border border-border-default rounded-base text-xs text-text-secondary transition-colors"
                  >
                    {v}
                  </button>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default FormulaTestingPage;
