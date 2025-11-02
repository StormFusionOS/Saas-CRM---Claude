/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Error handling utilities.
 *
 * Provides error code enum, human-readable message mapping,
 * and error response types matching the backend API.
 */

/**
 * Error codes matching backend ErrorCode enum.
 */
export enum ErrorCode {
  // Authentication errors (401)
  ERR_AUTH_INVALID_CREDENTIALS = "ERR_AUTH_INVALID_CREDENTIALS",
  ERR_AUTH_EXPIRED = "ERR_AUTH_EXPIRED",
  ERR_AUTH_MISSING = "ERR_AUTH_MISSING",
  ERR_AUTH_INVALID_TOKEN = "ERR_AUTH_INVALID_TOKEN",

  // Authorization errors (403)
  ERR_FORBIDDEN = "ERR_FORBIDDEN",
  ERR_FORBIDDEN_REALM = "ERR_FORBIDDEN_REALM",
  ERR_FORBIDDEN_INACTIVE = "ERR_FORBIDDEN_INACTIVE",

  // Resource errors (404)
  ERR_NOT_FOUND = "ERR_NOT_FOUND",
  ERR_RESOURCE_NOT_FOUND = "ERR_RESOURCE_NOT_FOUND",
  ERR_CONTACT_NOT_FOUND = "ERR_CONTACT_NOT_FOUND",
  ERR_LEAD_NOT_FOUND = "ERR_LEAD_NOT_FOUND",
  ERR_USER_NOT_FOUND = "ERR_USER_NOT_FOUND",

  // Validation errors (400)
  ERR_VALIDATION = "ERR_VALIDATION",
  ERR_DUPLICATE_EMAIL = "ERR_DUPLICATE_EMAIL",
  ERR_INVALID_INPUT = "ERR_INVALID_INPUT",
  ERR_MISSING_FIELD = "ERR_MISSING_FIELD",
  ERR_CONTACT_HAS_LEADS = "ERR_CONTACT_HAS_LEADS",

  // Webhook errors (403)
  ERR_WEBHOOK_SIGNATURE = "ERR_WEBHOOK_SIGNATURE",
  ERR_WEBHOOK_VERIFICATION = "ERR_WEBHOOK_VERIFICATION",
  ERR_WEBHOOK_INVALID_SECRET = "ERR_WEBHOOK_INVALID_SECRET",

  // Rate limiting (429)
  ERR_RATE_LIMIT = "ERR_RATE_LIMIT",
  ERR_RATE_LIMIT_EXCEEDED = "ERR_RATE_LIMIT_EXCEEDED",

  // Server errors (500)
  ERR_INTERNAL = "ERR_INTERNAL",
  ERR_DATABASE = "ERR_DATABASE",
  ERR_EXTERNAL_SERVICE = "ERR_EXTERNAL_SERVICE",
  ERR_INGESTION = "ERR_INGESTION",

  // Network/client errors
  ERR_NETWORK = "ERR_NETWORK",
  ERR_TIMEOUT = "ERR_TIMEOUT",
  ERR_UNKNOWN = "ERR_UNKNOWN",
}

/**
 * Error detail from API response.
 */
export interface ErrorDetail {
  code: ErrorCode;
  message: string;
  details?: Record<string, unknown>;
}

/**
 * Standard error response envelope from API.
 */
export interface ErrorResponse {
  error: ErrorDetail;
}

/**
 * User-friendly error messages for each error code.
 *
 * These messages are shown to end users in toasts and inline error displays.
 */
export const ERROR_MESSAGES: Record<ErrorCode, string> = {
  // Authentication errors
  [ErrorCode.ERR_AUTH_INVALID_CREDENTIALS]:
    "Invalid email or password. Please check your credentials and try again.",
  [ErrorCode.ERR_AUTH_EXPIRED]:
    "Your session has expired. Please log in again to continue.",
  [ErrorCode.ERR_AUTH_MISSING]:
    "You must be logged in to access this resource.",
  [ErrorCode.ERR_AUTH_INVALID_TOKEN]:
    "Your session is invalid. Please log in again.",

  // Authorization errors
  [ErrorCode.ERR_FORBIDDEN]:
    "You don't have permission to access this resource.",
  [ErrorCode.ERR_FORBIDDEN_REALM]:
    "You don't have permission to access this section. Please contact your administrator.",
  [ErrorCode.ERR_FORBIDDEN_INACTIVE]:
    "Your account is inactive. Please contact your administrator.",

  // Resource errors
  [ErrorCode.ERR_NOT_FOUND]:
    "The requested resource was not found.",
  [ErrorCode.ERR_RESOURCE_NOT_FOUND]:
    "The requested resource was not found.",
  [ErrorCode.ERR_CONTACT_NOT_FOUND]:
    "Contact not found. It may have been deleted.",
  [ErrorCode.ERR_LEAD_NOT_FOUND]:
    "Lead not found. It may have been deleted.",
  [ErrorCode.ERR_USER_NOT_FOUND]:
    "User not found.",

  // Validation errors
  [ErrorCode.ERR_VALIDATION]:
    "Please check your input and try again.",
  [ErrorCode.ERR_DUPLICATE_EMAIL]:
    "A contact with this email already exists.",
  [ErrorCode.ERR_INVALID_INPUT]:
    "The information you entered is invalid. Please check and try again.",
  [ErrorCode.ERR_MISSING_FIELD]:
    "Please fill in all required fields.",
  [ErrorCode.ERR_CONTACT_HAS_LEADS]:
    "Cannot delete this contact because it has associated leads. Please remove or reassign the leads first.",

  // Webhook errors
  [ErrorCode.ERR_WEBHOOK_SIGNATURE]:
    "Webhook signature verification failed.",
  [ErrorCode.ERR_WEBHOOK_VERIFICATION]:
    "Webhook verification failed.",
  [ErrorCode.ERR_WEBHOOK_INVALID_SECRET]:
    "Invalid webhook secret.",

  // Rate limiting
  [ErrorCode.ERR_RATE_LIMIT]:
    "Too many requests. Please wait a moment and try again.",
  [ErrorCode.ERR_RATE_LIMIT_EXCEEDED]:
    "You've made too many requests. Please wait a few minutes before trying again.",

  // Server errors
  [ErrorCode.ERR_INTERNAL]:
    "Something went wrong on our end. Please try again later.",
  [ErrorCode.ERR_DATABASE]:
    "A database error occurred. Please try again later.",
  [ErrorCode.ERR_EXTERNAL_SERVICE]:
    "An external service is currently unavailable. Please try again later.",
  [ErrorCode.ERR_INGESTION]:
    "Failed to process the request. Please try again.",

  // Network/client errors
  [ErrorCode.ERR_NETWORK]:
    "Network error. Please check your internet connection and try again.",
  [ErrorCode.ERR_TIMEOUT]:
    "The request timed out. Please try again.",
  [ErrorCode.ERR_UNKNOWN]:
    "An unexpected error occurred. Please try again.",
};

/**
 * Get user-friendly message for an error code.
 */
export function getErrorMessage(code: ErrorCode | string): string {
  return ERROR_MESSAGES[code as ErrorCode] || ERROR_MESSAGES[ErrorCode.ERR_UNKNOWN];
}

/**
 * Parse error from API response or generic Error object.
 */
export function parseError(error: unknown): ErrorDetail {
  // Handle axios error
  if (error && typeof error === "object" && "response" in error) {
    const axiosError = error as { response?: { data?: ErrorResponse; status?: number } };
    if (axiosError.response?.data?.error) {
      return axiosError.response.data.error;
    }

    // Handle non-standard error responses
    if (axiosError.response?.status === 401) {
      return {
        code: ErrorCode.ERR_AUTH_EXPIRED,
        message: getErrorMessage(ErrorCode.ERR_AUTH_EXPIRED),
      };
    }

    if (axiosError.response?.status === 403) {
      return {
        code: ErrorCode.ERR_FORBIDDEN,
        message: getErrorMessage(ErrorCode.ERR_FORBIDDEN),
      };
    }

    if (axiosError.response?.status === 404) {
      return {
        code: ErrorCode.ERR_NOT_FOUND,
        message: getErrorMessage(ErrorCode.ERR_NOT_FOUND),
      };
    }

    if (axiosError.response?.status === 429) {
      return {
        code: ErrorCode.ERR_RATE_LIMIT,
        message: getErrorMessage(ErrorCode.ERR_RATE_LIMIT),
      };
    }

    if (axiosError.response?.status && axiosError.response.status >= 500) {
      return {
        code: ErrorCode.ERR_INTERNAL,
        message: getErrorMessage(ErrorCode.ERR_INTERNAL),
      };
    }
  }

  // Handle network errors
  if (error && typeof error === "object" && "message" in error) {
    const errorMessage = (error as { message: string }).message.toLowerCase();
    if (errorMessage.includes("network") || errorMessage.includes("failed to fetch")) {
      return {
        code: ErrorCode.ERR_NETWORK,
        message: getErrorMessage(ErrorCode.ERR_NETWORK),
      };
    }

    if (errorMessage.includes("timeout")) {
      return {
        code: ErrorCode.ERR_TIMEOUT,
        message: getErrorMessage(ErrorCode.ERR_TIMEOUT),
      };
    }
  }

  // Fallback to unknown error
  return {
    code: ErrorCode.ERR_UNKNOWN,
    message: getErrorMessage(ErrorCode.ERR_UNKNOWN),
  };
}

/**
 * Generate a unique error ID for support purposes.
 */
export function generateErrorId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 7);
  return `err_${timestamp}_${random}`.toUpperCase();
}
