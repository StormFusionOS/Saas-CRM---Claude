/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Prompt Runner Page
 * Deep research prompts with OpenAI API integration and knowledge base storage
 */

import React, { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  category: string;
  created_at: string;
  updated_at: string;
}

interface PromptRun {
  id: string;
  prompt_id: string;
  prompt_name: string;
  input: string;
  response: string;
  tokens_used: number;
  cost: number;
  duration_ms: number;
  model: string;
  created_at: string;
  saved_to_kb: boolean;
}

const PromptRunnerPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'library' | 'runner' | 'history' | 'knowledge'>('library');
  const [selectedPrompt, setSelectedPrompt] = useState<PromptTemplate | null>(null);
  const [promptInput, setPromptInput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [runHistory, setRunHistory] = useState<PromptRun[]>([]);

  // Mock data - will be replaced with API calls
  const mockPrompts: PromptTemplate[] = [
    {
      id: '1',
      name: 'Competitor Analysis',
      description: 'Deep analysis of competitor strategies and positioning',
      template: 'Analyze the following competitor: {{competitor_name}}\n\nFocus on: {{focus_areas}}',
      category: 'Research',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: '2',
      name: 'Market Trends',
      description: 'Identify emerging market trends in a specific industry',
      template: 'Research market trends for: {{industry}}\n\nTime period: {{time_period}}',
      category: 'Research',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];

  const handleRunPrompt = async () => {
    if (!selectedPrompt || !promptInput.trim()) return;

    setIsRunning(true);
    // Simulate API call
    setTimeout(() => {
      const newRun: PromptRun = {
        id: Date.now().toString(),
        prompt_id: selectedPrompt.id,
        prompt_name: selectedPrompt.name,
        input: promptInput,
        response: 'This is a simulated response from OpenAI API. In production, this would be the actual AI-generated response.',
        tokens_used: 1250,
        cost: 0.025,
        duration_ms: 3500,
        model: 'gpt-4',
        created_at: new Date().toISOString(),
        saved_to_kb: false,
      };
      setRunHistory([newRun, ...runHistory]);
      setIsRunning(false);
      setActiveTab('history');
    }, 2000);
  };

  const handleSaveToKnowledgeBase = (runId: string) => {
    setRunHistory(runHistory.map(run =>
      run.id === runId ? { ...run, saved_to_kb: true } : run
    ));
  };

  const handleDeleteRun = (runId: string) => {
    setRunHistory(runHistory.filter(run => run.id !== runId));
  };

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Prompt Runner</h1>
        <p className="text-sm text-text-muted mt-1">
          Deep research prompts with OpenAI API integration and knowledge base storage
        </p>
      </div>

      {/* Main Content */}
      <main className="p-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Saved Prompts</h3>
            <p className="text-4xl font-display font-bold text-primary">{mockPrompts.length}</p>
            <div className="mt-2 text-xs text-text-muted">In library</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Total Runs</h3>
            <p className="text-4xl font-display font-bold text-success">{runHistory.length}</p>
            <div className="mt-2 text-xs text-text-muted">All time</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">In Knowledge Base</h3>
            <p className="text-4xl font-display font-bold text-electric-cyan">
              {runHistory.filter(r => r.saved_to_kb).length}
            </p>
            <div className="mt-2 text-xs text-text-muted">Saved responses</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Total Cost</h3>
            <p className="text-4xl font-display font-bold text-warning">
              ${runHistory.reduce((acc, r) => acc + r.cost, 0).toFixed(2)}
            </p>
            <div className="mt-2 text-xs text-text-muted">OpenAI API</div>
          </Card>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-white/10">
          <button
            onClick={() => setActiveTab('library')}
            className={`px-6 py-3 font-medium transition-all border-b-2 ${
              activeTab === 'library'
                ? 'text-primary border-primary'
                : 'text-text-muted border-transparent hover:text-text-secondary'
            }`}
          >
            Prompt Library
          </button>
          <button
            onClick={() => setActiveTab('runner')}
            className={`px-6 py-3 font-medium transition-all border-b-2 ${
              activeTab === 'runner'
                ? 'text-primary border-primary'
                : 'text-text-muted border-transparent hover:text-text-secondary'
            }`}
          >
            Run Prompt
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-6 py-3 font-medium transition-all border-b-2 ${
              activeTab === 'history'
                ? 'text-primary border-primary'
                : 'text-text-muted border-transparent hover:text-text-secondary'
            }`}
          >
            Run History ({runHistory.length})
          </button>
          <button
            onClick={() => setActiveTab('knowledge')}
            className={`px-6 py-3 font-medium transition-all border-b-2 ${
              activeTab === 'knowledge'
                ? 'text-primary border-primary'
                : 'text-text-muted border-transparent hover:text-text-secondary'
            }`}
          >
            Knowledge Base ({runHistory.filter(r => r.saved_to_kb).length})
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'library' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mockPrompts.map((prompt) => (
              <Card key={prompt.id} padding="lg" className="glow-hover cursor-pointer" onClick={() => {
                setSelectedPrompt(prompt);
                setActiveTab('runner');
              }}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">{prompt.name}</h3>
                    <span className="inline-block mt-1 px-2 py-1 text-xs rounded bg-primary/10 text-primary">
                      {prompt.category}
                    </span>
                  </div>
                  <button className="text-text-muted hover:text-text-primary">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                    </svg>
                  </button>
                </div>
                <p className="text-sm text-text-secondary mb-4">{prompt.description}</p>
                <div className="p-3 bg-white/5 rounded font-mono text-xs text-text-muted">
                  {prompt.template.substring(0, 100)}...
                </div>
              </Card>
            ))}

            <Card padding="lg" className="border-2 border-dashed border-white/20 hover:border-primary/50 cursor-pointer transition-all">
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <svg className="w-12 h-12 text-text-muted mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <h3 className="text-lg font-semibold text-text-primary mb-2">Create New Prompt</h3>
                <p className="text-sm text-text-muted">Add a new research prompt template</p>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'runner' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card padding="lg">
                <h2 className="text-xl font-display font-semibold mb-4">Execute Prompt</h2>

                {selectedPrompt ? (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">
                        Selected Prompt
                      </label>
                      <div className="p-4 bg-white/5 rounded">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold text-text-primary">{selectedPrompt.name}</span>
                          <button
                            onClick={() => setSelectedPrompt(null)}
                            className="text-xs text-text-muted hover:text-error"
                          >
                            Clear
                          </button>
                        </div>
                        <p className="text-sm text-text-muted">{selectedPrompt.description}</p>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">
                        Prompt Input
                      </label>
                      <textarea
                        value={promptInput}
                        onChange={(e) => setPromptInput(e.target.value)}
                        className="w-full h-64 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-text-primary placeholder-text-muted focus:outline-none focus:border-primary/50 font-mono text-sm resize-none"
                        placeholder="Enter your prompt input here... You can use variables from the template or write a custom prompt."
                      />
                    </div>

                    <div className="flex gap-3">
                      <Button
                        variant="primary"
                        onClick={handleRunPrompt}
                        disabled={isRunning || !promptInput.trim()}
                        className="flex-1"
                      >
                        {isRunning ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Running...
                          </>
                        ) : (
                          'Run Prompt'
                        )}
                      </Button>
                      <Button variant="secondary">
                        Save Draft
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <svg className="w-16 h-16 mx-auto text-text-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-lg text-text-secondary font-medium mb-2">No Prompt Selected</p>
                    <p className="text-sm text-text-muted">Select a prompt from the library to get started</p>
                  </div>
                )}
              </Card>
            </div>

            <div>
              <Card padding="lg">
                <h3 className="text-lg font-semibold mb-4">Configuration</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Model
                    </label>
                    <select className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-primary/50">
                      <option>gpt-4</option>
                      <option>gpt-4-turbo</option>
                      <option>gpt-3.5-turbo</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Temperature: 0.7
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      defaultValue="0.7"
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Max Tokens
                    </label>
                    <input
                      type="number"
                      defaultValue="2000"
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-primary/50"
                    />
                  </div>

                  <div className="pt-4 border-t border-white/10">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" defaultChecked className="w-4 h-4" />
                      <span className="text-sm text-text-secondary">Auto-save to Knowledge Base</span>
                    </label>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Run History</h2>
            {runHistory.length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-text-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-lg text-text-secondary font-medium mb-2">No Runs Yet</p>
                <p className="text-sm text-text-muted">Your prompt execution history will appear here</p>
              </div>
            ) : (
              <div className="space-y-4">
                {runHistory.map((run) => (
                  <div key={run.id} className="p-4 bg-white/5 rounded-lg border border-white/10">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-text-primary">{run.prompt_name}</h3>
                        <p className="text-xs text-text-muted mt-1">
                          {new Date(run.created_at).toLocaleString()} • {run.model} • {run.tokens_used} tokens • ${run.cost.toFixed(3)}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        {run.saved_to_kb ? (
                          <span className="px-2 py-1 text-xs rounded bg-success/10 text-success">
                            In KB
                          </span>
                        ) : (
                          <button
                            onClick={() => handleSaveToKnowledgeBase(run.id)}
                            className="px-3 py-1 text-xs rounded bg-primary/10 text-primary hover:bg-primary/20 transition-all"
                          >
                            Save to KB
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteRun(run.id)}
                          className="px-3 py-1 text-xs rounded bg-error/10 text-error hover:bg-error/20 transition-all"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                    <div className="mb-3">
                      <p className="text-xs font-medium text-text-secondary mb-1">Input:</p>
                      <p className="text-sm text-text-muted font-mono bg-white/5 p-2 rounded">
                        {run.input.substring(0, 150)}...
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-text-secondary mb-1">Response:</p>
                      <p className="text-sm text-text-primary bg-white/5 p-2 rounded">
                        {run.response}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {activeTab === 'knowledge' && (
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Knowledge Base</h2>
            {runHistory.filter(r => r.saved_to_kb).length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-text-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
                </svg>
                <p className="text-lg text-text-secondary font-medium mb-2">No Saved Responses</p>
                <p className="text-sm text-text-muted">Save responses from your run history to build your knowledge base</p>
              </div>
            ) : (
              <div className="space-y-4">
                {runHistory.filter(r => r.saved_to_kb).map((run) => (
                  <div key={run.id} className="p-4 bg-white/5 rounded-lg border border-electric-cyan/20">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-text-primary">{run.prompt_name}</h3>
                        <p className="text-xs text-text-muted mt-1">
                          Added {new Date(run.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={() => handleDeleteRun(run.id)}
                        className="px-3 py-1 text-xs rounded bg-error/10 text-error hover:bg-error/20 transition-all"
                      >
                        Remove from KB
                      </button>
                    </div>
                    <div className="p-3 bg-white/5 rounded text-sm text-text-primary">
                      {run.response}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}
      </main>
    </div>
  );
};

export default PromptRunnerPage;
