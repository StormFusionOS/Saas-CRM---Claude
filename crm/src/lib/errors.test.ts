/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Tests for error handling utilities.
 */

import { describe, it, expect } from "vitest";
import {
  ErrorCode,
  getErrorMessage,
  parseError,
  generateErrorId,
  ERROR_MESSAGES,
} from "./errors";

describe("Error Handling", () => {
  describe("getErrorMessage", () => {
    it("should return correct message for auth errors", () => {
      const message = getErrorMessage(ErrorCode.ERR_AUTH_INVALID_CREDENTIALS);
      expect(message).toBe(
        "Invalid email or password. Please check your credentials and try again."
      );
    });

    it("should return correct message for expired session", () => {
      const message = getErrorMessage(ErrorCode.ERR_AUTH_EXPIRED);
      expect(message).toBe("Your session has expired. Please log in again to continue.");
    });

    it("should return correct message for forbidden access", () => {
      const message = getErrorMessage(ErrorCode.ERR_FORBIDDEN);
      expect(message).toBe("You don't have permission to access this resource.");
    });

    it("should return correct message for not found errors", () => {
      const message = getErrorMessage(ErrorCode.ERR_LEAD_NOT_FOUND);
      expect(message).toBe("Lead not found. It may have been deleted.");
    });

    it("should return correct message for validation errors", () => {
      const message = getErrorMessage(ErrorCode.ERR_DUPLICATE_EMAIL);
      expect(message).toBe("A contact with this email already exists.");
    });

    it("should return correct message for rate limit errors", () => {
      const message = getErrorMessage(ErrorCode.ERR_RATE_LIMIT);
      expect(message).toBe("Too many requests. Please wait a moment and try again.");
    });

    it("should return default message for unknown error codes", () => {
      const message = getErrorMessage("UNKNOWN_CODE" as ErrorCode);
      expect(message).toBe("An unexpected error occurred. Please try again.");
    });
  });

  describe("parseError", () => {
    it("should parse standard error response from API", () => {
      const axiosError = {
        response: {
          data: {
            error: {
              code: ErrorCode.ERR_AUTH_EXPIRED,
              message: "Your session has expired",
              details: {},
            },
          },
        },
      };

      const parsed = parseError(axiosError);
      expect(parsed.code).toBe(ErrorCode.ERR_AUTH_EXPIRED);
      expect(parsed.message).toBe("Your session has expired");
    });

    it("should map 401 status to auth error when no error envelope", () => {
      const axiosError = {
        response: {
          status: 401,
        },
      };

      const parsed = parseError(axiosError);
      expect(parsed.code).toBe(ErrorCode.ERR_AUTH_EXPIRED);
    });

    it("should map 403 status to forbidden error", () => {
      const axiosError = {
        response: {
          status: 403,
        },
      };

      const parsed = parseError(axiosError);
      expect(parsed.code).toBe(ErrorCode.ERR_FORBIDDEN);
    });

    it("should map 404 status to not found error", () => {
      const axiosError = {
        response: {
          status: 404,
        },
      };

      const parsed = parseError(axiosError);
      expect(parsed.code).toBe(ErrorCode.ERR_NOT_FOUND);
    });

    it("should map 429 status to rate limit error", () => {
      const axiosError = {
        response: {
          status: 429,
        },
      };

      const parsed = parseError(axiosError);
      expect(parsed.code).toBe(ErrorCode.ERR_RATE_LIMIT);
    });

    it("should map 500+ status to internal error", () => {
      const axiosError = {
        response: {
          status: 500,
        },
      };

      const parsed = parseError(axiosError);
      expect(parsed.code).toBe(ErrorCode.ERR_INTERNAL);
    });

    it("should detect network errors from message", () => {
      const networkError = {
        message: "Network error occurred",
      };

      const parsed = parseError(networkError);
      expect(parsed.code).toBe(ErrorCode.ERR_NETWORK);
    });

    it("should detect timeout errors from message", () => {
      const timeoutError = {
        message: "Request timeout",
      };

      const parsed = parseError(timeoutError);
      expect(parsed.code).toBe(ErrorCode.ERR_TIMEOUT);
    });

    it("should fallback to unknown error for unrecognized errors", () => {
      const unknownError = {
        message: "Something weird happened",
      };

      const parsed = parseError(unknownError);
      expect(parsed.code).toBe(ErrorCode.ERR_UNKNOWN);
    });
  });

  describe("generateErrorId", () => {
    it("should generate unique error IDs", () => {
      const id1 = generateErrorId();
      const id2 = generateErrorId();

      expect(id1).toMatch(/^ERR_[A-Z0-9]+_[A-Z0-9]+$/);
      expect(id2).toMatch(/^ERR_[A-Z0-9]+_[A-Z0-9]+$/);
      expect(id1).not.toBe(id2);
    });

    it("should generate IDs with consistent format", () => {
      const id = generateErrorId();
      const parts = id.split("_");

      expect(parts[0]).toBe("ERR");
      expect(parts).toHaveLength(3); // ERR_timestamp_random
    });
  });

  describe("ERROR_MESSAGES coverage", () => {
    it("should have messages for all error codes", () => {
      // Get all error code values
      const errorCodes = Object.values(ErrorCode);

      // Filter out network/client errors as they're not from backend
      const backendErrors = errorCodes.filter(
        (code) => !["ERR_NETWORK", "ERR_TIMEOUT", "ERR_UNKNOWN"].includes(code)
      );

      backendErrors.forEach((code) => {
        const message = ERROR_MESSAGES[code];
        expect(message).toBeDefined();
        expect(message.length).toBeGreaterThan(0);
      });
    });

    it("should have user-friendly messages (not technical)", () => {
      // Check a few messages to ensure they're user-friendly
      expect(ERROR_MESSAGES[ErrorCode.ERR_AUTH_EXPIRED]).not.toContain("token");
      expect(ERROR_MESSAGES[ErrorCode.ERR_AUTH_EXPIRED]).not.toContain("JWT");

      expect(ERROR_MESSAGES[ErrorCode.ERR_INTERNAL]).not.toContain("exception");
      expect(ERROR_MESSAGES[ErrorCode.ERR_INTERNAL]).not.toContain("stack trace");
    });
  });
});
