/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Error Display Components.
 *
 * Provides toast notifications and inline error displays with
 * user-friendly messages and copy-to-clipboard error IDs.
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { ErrorDetail, ErrorCode, getErrorMessage, generateErrorId } from "../lib/errors";

/**
 * Error with generated ID for support.
 */
export interface DisplayError extends ErrorDetail {
  id: string;
  timestamp: Date;
}

/**
 * Error context for managing global error state.
 */
interface ErrorContextType {
  errors: DisplayError[];
  showError: (error: ErrorDetail) => string;
  dismissError: (errorId: string) => void;
  clearAll: () => void;
}

const ErrorContext = createContext<ErrorContextType | null>(null);

/**
 * Error Provider Component.
 *
 * Wraps the app to provide error management context.
 */
export function ErrorProvider({ children }: { children: React.ReactNode }) {
  const [errors, setErrors] = useState<DisplayError[]>([]);

  const showError = useCallback((error: ErrorDetail): string => {
    const displayError: DisplayError = {
      ...error,
      id: generateErrorId(),
      timestamp: new Date(),
    };

    setErrors((prev) => [...prev, displayError]);

    // Auto-dismiss after 10 seconds for non-critical errors
    if (!error.code.startsWith("ERR_AUTH") && !error.code.startsWith("ERR_FORBIDDEN")) {
      setTimeout(() => {
        dismissError(displayError.id);
      }, 10000);
    }

    return displayError.id;
  }, []);

  const dismissError = useCallback((errorId: string) => {
    setErrors((prev) => prev.filter((e) => e.id !== errorId));
  }, []);

  const clearAll = useCallback(() => {
    setErrors([]);
  }, []);

  return (
    <ErrorContext.Provider value={{ errors, showError, dismissError, clearAll }}>
      {children}
      <ErrorToastContainer errors={errors} onDismiss={dismissError} />
    </ErrorContext.Provider>
  );
}

/**
 * Hook to access error context.
 */
export function useErrors() {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error("useErrors must be used within ErrorProvider");
  }
  return context;
}

/**
 * Toast Container Component.
 *
 * Displays errors as toast notifications in the top-right corner.
 */
function ErrorToastContainer({
  errors,
  onDismiss,
}: {
  errors: DisplayError[];
  onDismiss: (id: string) => void;
}) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      {errors.map((error) => (
        <ErrorToast key={error.id} error={error} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

/**
 * Individual Toast Component.
 */
function ErrorToast({
  error,
  onDismiss,
}: {
  error: DisplayError;
  onDismiss: (id: string) => void;
}) {
  const [copied, setCopied] = useState(false);

  const copyErrorId = useCallback(() => {
    navigator.clipboard.writeText(error.id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [error.id]);

  // Determine severity based on error code
  const severity = getSeverity(error.code);

  return (
    <div
      className={`
        rounded-lg shadow-lg p-4 animate-slide-in
        ${severity === "error" ? "bg-red-900/90 border border-red-700" : ""}
        ${severity === "warning" ? "bg-yellow-900/90 border border-yellow-700" : ""}
        ${severity === "info" ? "bg-blue-900/90 border border-blue-700" : ""}
        backdrop-blur-sm
      `}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0 mt-0.5">
          {severity === "error" && (
            <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          )}
          {severity === "warning" && (
            <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          )}
          {severity === "info" && (
            <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white mb-1">{error.message}</p>

          {/* Error ID */}
          <div className="flex items-center gap-2 mt-2">
            <button
              onClick={copyErrorId}
              className="text-xs text-gray-400 hover:text-gray-300 flex items-center gap-1 transition-colors"
              title="Click to copy error ID"
            >
              <span className="font-mono">{error.id}</span>
              {copied ? (
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                  <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                </svg>
              )}
            </button>
            {copied && <span className="text-xs text-green-400">Copied!</span>}
          </div>

          {/* Validation errors details */}
          {error.details?.validation_errors && Array.isArray(error.details.validation_errors) && (
            <ul className="mt-2 text-xs text-gray-300 list-disc list-inside space-y-1">
              {(error.details.validation_errors as Array<{ field: string; message: string }>).map(
                (ve, idx) => (
                  <li key={idx}>
                    <span className="font-medium">{ve.field}:</span> {ve.message}
                  </li>
                )
              )}
            </ul>
          )}
        </div>

        {/* Close button */}
        <button
          onClick={() => onDismiss(error.id)}
          className="flex-shrink-0 text-gray-400 hover:text-white transition-colors"
          aria-label="Dismiss error"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

/**
 * Inline Error Component.
 *
 * Displays an error inline within a form or page section.
 */
export function InlineError({ error }: { error: ErrorDetail | null }) {
  const [copied, setCopied] = useState(false);
  const errorId = React.useMemo(() => generateErrorId(), [error]);

  const copyErrorId = useCallback(() => {
    navigator.clipboard.writeText(errorId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [errorId]);

  if (!error) return null;

  const severity = getSeverity(error.code);

  return (
    <div
      className={`
        rounded-md p-4
        ${severity === "error" ? "bg-red-900/20 border border-red-700/50" : ""}
        ${severity === "warning" ? "bg-yellow-900/20 border border-yellow-700/50" : ""}
        ${severity === "info" ? "bg-blue-900/20 border border-blue-700/50" : ""}
      `}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          {severity === "error" && (
            <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>

        <div className="flex-1">
          <p className="text-sm text-white">{error.message}</p>

          <button
            onClick={copyErrorId}
            className="mt-2 text-xs text-gray-400 hover:text-gray-300 flex items-center gap-1 transition-colors"
            title="Click to copy error ID"
          >
            <span className="font-mono">{errorId}</span>
            {copied ? (
              <span className="text-green-400">✓ Copied</span>
            ) : (
              <span>Copy error ID</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Determine severity level based on error code.
 */
function getSeverity(code: ErrorCode | string): "error" | "warning" | "info" {
  const codeStr = code.toString();

  if (
    codeStr.startsWith("ERR_AUTH") ||
    codeStr.startsWith("ERR_FORBIDDEN") ||
    codeStr.includes("NOT_FOUND") ||
    codeStr.includes("INTERNAL") ||
    codeStr.includes("DATABASE")
  ) {
    return "error";
  }

  if (
    codeStr.includes("RATE_LIMIT") ||
    codeStr.includes("VALIDATION") ||
    codeStr.includes("DUPLICATE")
  ) {
    return "warning";
  }

  return "info";
}
