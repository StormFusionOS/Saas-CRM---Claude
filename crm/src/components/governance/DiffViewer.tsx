/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Diff Viewer Component
 * Accessible side-by-side comparison of old vs new values
 */

import React, { useMemo } from 'react';
import { Minus, Plus, ArrowRight } from 'lucide-react';

interface DiffViewerProps {
  oldValue: any;
  newValue: any;
  label?: string;
  className?: string;
}

/**
 * Deep comparison to highlight differences
 */
function getDifferences(oldVal: any, newVal: any): {
  added: Set<string>;
  removed: Set<string>;
  changed: Set<string>;
} {
  const added = new Set<string>();
  const removed = new Set<string>();
  const changed = new Set<string>();

  if (typeof oldVal !== 'object' || typeof newVal !== 'object' || oldVal === null || newVal === null) {
    if (oldVal !== newVal) {
      changed.add('_root');
    }
    return { added, removed, changed };
  }

  const oldKeys = new Set(Object.keys(oldVal));
  const newKeys = new Set(Object.keys(newVal));

  // Find added keys
  for (const key of newKeys) {
    if (!oldKeys.has(key)) {
      added.add(key);
    }
  }

  // Find removed keys
  for (const key of oldKeys) {
    if (!newKeys.has(key)) {
      removed.add(key);
    }
  }

  // Find changed keys
  for (const key of oldKeys) {
    if (newKeys.has(key)) {
      const oldV = oldVal[key];
      const newV = newVal[key];

      if (JSON.stringify(oldV) !== JSON.stringify(newV)) {
        changed.add(key);
      }
    }
  }

  return { added, removed, changed };
}

/**
 * Format value for display
 */
function formatValue(value: any): string {
  if (value === null) return 'null';
  if (value === undefined) return 'undefined';
  if (typeof value === 'string') return value;
  return JSON.stringify(value, null, 2);
}

/**
 * Render object comparison
 */
function ObjectDiff({ oldValue, newValue }: { oldValue: any; newValue: any }) {
  const diffs = useMemo(() => getDifferences(oldValue, newValue), [oldValue, newValue]);

  if (typeof oldValue !== 'object' || typeof newValue !== 'object' || oldValue === null || newValue === null) {
    return <SimpleDiff oldValue={oldValue} newValue={newValue} />;
  }

  const allKeys = new Set([...Object.keys(oldValue || {}), ...Object.keys(newValue || {})]);
  const sortedKeys = Array.from(allKeys).sort();

  return (
    <div className="space-y-2">
      {sortedKeys.map((key) => {
        const isAdded = diffs.added.has(key);
        const isRemoved = diffs.removed.has(key);
        const isChanged = diffs.changed.has(key);

        if (isRemoved) {
          return (
            <div key={key} className="group rounded-lg border border-error/30 bg-error/5 p-3">
              <div className="flex items-center gap-2 mb-2">
                <Minus className="w-4 h-4 text-error" />
                <span className="font-mono text-sm text-error font-medium">{key}</span>
                <span className="text-xs text-error/70 ml-auto">removed</span>
              </div>
              <pre className="text-sm text-text-secondary pl-6">
                {formatValue(oldValue[key])}
              </pre>
            </div>
          );
        }

        if (isAdded) {
          return (
            <div key={key} className="group rounded-lg border border-success/30 bg-success/5 p-3">
              <div className="flex items-center gap-2 mb-2">
                <Plus className="w-4 h-4 text-success" />
                <span className="font-mono text-sm text-success font-medium">{key}</span>
                <span className="text-xs text-success/70 ml-auto">added</span>
              </div>
              <pre className="text-sm text-text-secondary pl-6">
                {formatValue(newValue[key])}
              </pre>
            </div>
          );
        }

        if (isChanged) {
          return (
            <div key={key} className="group rounded-lg border border-warning/30 bg-warning/5 p-3">
              <div className="flex items-center gap-2 mb-2">
                <ArrowRight className="w-4 h-4 text-warning" />
                <span className="font-mono text-sm text-warning font-medium">{key}</span>
                <span className="text-xs text-warning/70 ml-auto">changed</span>
              </div>
              <div className="pl-6 space-y-2">
                <div>
                  <div className="text-xs text-text-muted mb-1">Before:</div>
                  <pre className="text-sm text-text-secondary bg-bg-base rounded p-2">
                    {formatValue(oldValue[key])}
                  </pre>
                </div>
                <div>
                  <div className="text-xs text-text-muted mb-1">After:</div>
                  <pre className="text-sm text-text-secondary bg-bg-base rounded p-2">
                    {formatValue(newValue[key])}
                  </pre>
                </div>
              </div>
            </div>
          );
        }

        // Unchanged
        return (
          <div key={key} className="group rounded-lg border border-white/10 bg-white/5 p-3 opacity-60">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-sm text-text-muted">{key}</span>
              <span className="text-xs text-text-muted/50 ml-auto">unchanged</span>
            </div>
            <pre className="text-sm text-text-muted pl-6">
              {formatValue(oldValue[key])}
            </pre>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Simple side-by-side diff for primitive values
 */
function SimpleDiff({ oldValue, newValue }: { oldValue: any; newValue: any }) {
  const oldStr = formatValue(oldValue);
  const newStr = formatValue(newValue);
  const isChanged = oldStr !== newStr;

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Current Value */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <div className="text-sm font-medium text-text-secondary">Current</div>
          {isChanged && <Minus className="w-3 h-3 text-error" />}
        </div>
        <div
          className={`rounded-lg border p-4 ${
            isChanged
              ? 'border-error/30 bg-error/5'
              : 'border-white/10 bg-white/5'
          }`}
        >
          <pre className="text-sm text-text-primary whitespace-pre-wrap break-words">
            {oldStr}
          </pre>
        </div>
      </div>

      {/* Proposed Value */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <div className="text-sm font-medium text-text-secondary">Proposed</div>
          {isChanged && <Plus className="w-3 h-3 text-success" />}
        </div>
        <div
          className={`rounded-lg border p-4 ${
            isChanged
              ? 'border-success/30 bg-success/5'
              : 'border-white/10 bg-white/5'
          }`}
        >
          <pre className="text-sm text-text-primary whitespace-pre-wrap break-words">
            {newStr}
          </pre>
        </div>
      </div>
    </div>
  );
}

/**
 * Main diff viewer component
 */
const DiffViewer: React.FC<DiffViewerProps> = ({ oldValue, newValue, label, className = '' }) => {
  const isObjectDiff = useMemo(() => {
    return (
      typeof oldValue === 'object' &&
      typeof newValue === 'object' &&
      oldValue !== null &&
      newValue !== null &&
      !Array.isArray(oldValue) &&
      !Array.isArray(newValue)
    );
  }, [oldValue, newValue]);

  return (
    <div className={`space-y-4 ${className}`} role="region" aria-label={label || 'Difference viewer'}>
      {label && (
        <h3 className="text-lg font-display font-semibold text-text-primary">{label}</h3>
      )}

      {isObjectDiff ? (
        <ObjectDiff oldValue={oldValue} newValue={newValue} />
      ) : (
        <SimpleDiff oldValue={oldValue} newValue={newValue} />
      )}
    </div>
  );
};

export default DiffViewer;
