/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * E2E Flow Test: Login → Dashboard
 *
 * Tests the complete user flow from login to viewing the ops dashboard
 * without a real browser (using happy-dom/jsdom).
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { AuthProvider, useAuth } from "../lib/auth-context";
import LoginPage from "../pages/LoginPage";
import DashboardPage from "../pages/DashboardPage";

// Mock axios
vi.mock("axios");
const mockedAxios = vi.mocked(axios, true);

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
  configurable: true,
});

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Test app that mimics the real routing structure
function TestApp() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

describe("E2E Flow: Login → Dashboard", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorageMock.clear();

    // Reset axios mocks
    vi.clearAllMocks();

    // Mock axios.create to return a mock instance
    mockedAxios.create = vi.fn(() => ({
      post: vi.fn(),
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
    })) as any;
  });

  it("should complete full login flow and display ops dashboard", async () => {
    // Mock successful login API response
    const mockToken = "mock_jwt_token_ops_xyz789";
    const mockPost = vi.fn().mockResolvedValue({
      data: {
        access_token: mockToken,
        token_type: "bearer",
      },
    });

    mockedAxios.create = vi.fn(() => ({
      post: mockPost,
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
    })) as any;

    // Render the full app
    render(<TestApp />);

    // STEP 1: Verify we're on the login page
    expect(screen.getByText("Ops Console")).toBeInTheDocument();
    expect(screen.getByText("Operations & Monitoring")).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();

    // STEP 2: Fill in login credentials (default values)
    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    // Inputs should have default values
    expect(emailInput.value).toBe("Nathan@RiverCityClean.com");
    expect(passwordInput.value).toBe("password123");

    // STEP 3: Submit the login form
    fireEvent.click(submitButton);

    // STEP 4: Verify API was called with correct credentials
    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith("/auth/login", {
        email: "Nathan@RiverCityClean.com",
        password: "password123",
      });
    });

    // STEP 5: Verify token is stored in localStorage
    await waitFor(() => {
      expect(localStorageMock.getItem("auth_token")).toBe(mockToken);
    });

    // STEP 6: Wait for navigation to dashboard
    await waitFor(() => {
      expect(screen.getByText("Ops Dashboard")).toBeInTheDocument();
    });

    // STEP 7: Verify protected layout renders with metrics/gauges
    // The dashboard has 3 metric cards

    // Services gauge
    expect(screen.getByText("Services")).toBeInTheDocument();
    expect(screen.getByText("12 / 12")).toBeInTheDocument();

    // Alerts gauge
    expect(screen.getByText("Alerts")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();

    // CPU Usage gauge
    expect(screen.getByText("CPU Usage")).toBeInTheDocument();
    expect(screen.getByText("45%")).toBeInTheDocument();
  });

  it("should protect dashboard route when not authenticated", () => {
    // Don't mock login API - just render without logging in

    mockedAxios.create = vi.fn(() => ({
      post: vi.fn(),
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
    })) as any;

    // Render app starting at dashboard route
    window.history.pushState({}, "", "/dashboard");
    render(<TestApp />);

    // Should be redirected to login
    expect(screen.getByText("Ops Console")).toBeInTheDocument();
    expect(screen.queryByText("Ops Dashboard")).not.toBeInTheDocument();
  });

  it("should show error message on failed login", async () => {
    // Mock failed login API response
    const mockPost = vi.fn().mockRejectedValue({
      response: {
        data: {
          detail: "Invalid email or password",
        },
        status: 401,
      },
    });

    mockedAxios.create = vi.fn(() => ({
      post: mockPost,
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
    })) as any;

    render(<TestApp />);

    // Submit login form
    const submitButton = screen.getByRole("button", { name: /sign in/i });
    fireEvent.click(submitButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText("Invalid email or password")).toBeInTheDocument();
    });

    // Verify we're still on login page
    expect(screen.getByText("Ops Console")).toBeInTheDocument();

    // Verify no token was stored
    expect(localStorageMock.getItem("auth_token")).toBeNull();
  });

  it("should persist authentication across page reloads", () => {
    // Set token in localStorage (simulating previous login)
    const existingToken = "existing_ops_token_xyz";
    localStorageMock.setItem("auth_token", existingToken);

    mockedAxios.create = vi.fn(() => ({
      post: vi.fn(),
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
    })) as any;

    // Navigate directly to dashboard
    window.history.pushState({}, "", "/dashboard");
    render(<TestApp />);

    // Should render dashboard without login
    expect(screen.getByText("Ops Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Services")).toBeInTheDocument();
    expect(screen.queryByText("Ops Console")).not.toBeInTheDocument();
  });

  it("should display all operational metrics in correct format", async () => {
    // Mock successful login
    const mockToken = "mock_token";
    const mockPost = vi.fn().mockResolvedValue({
      data: {
        access_token: mockToken,
        token_type: "bearer",
      },
    });

    mockedAxios.create = vi.fn(() => ({
      post: mockPost,
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
    })) as any;

    render(<TestApp />);

    // Login
    const submitButton = screen.getByRole("button", { name: /sign in/i });
    fireEvent.click(submitButton);

    // Wait for dashboard
    await waitFor(() => {
      expect(screen.getByText("Ops Dashboard")).toBeInTheDocument();
    });

    // Verify all 3 operational metrics are displayed
    const opsMetrics = [
      { label: "Services", value: "12 / 12" },
      { label: "Alerts", value: "3" },
      { label: "CPU Usage", value: "45%" },
    ];

    opsMetrics.forEach((metric) => {
      expect(screen.getByText(metric.label)).toBeInTheDocument();
      expect(screen.getByText(metric.value)).toBeInTheDocument();
    });
  });

  it("should render token in memory after login", async () => {
    const mockToken = "in_memory_token_test";
    const mockPost = vi.fn().mockResolvedValue({
      data: {
        access_token: mockToken,
        token_type: "bearer",
      },
    });

    mockedAxios.create = vi.fn(() => ({
      post: mockPost,
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
    })) as any;

    render(<TestApp />);

    // Login
    const submitButton = screen.getByRole("button", { name: /sign in/i });
    fireEvent.click(submitButton);

    // Wait for successful login
    await waitFor(() => {
      expect(screen.getByText("Ops Dashboard")).toBeInTheDocument();
    });

    // Verify token is in localStorage (memory)
    expect(localStorageMock.getItem("auth_token")).toBe(mockToken);
  });
});
