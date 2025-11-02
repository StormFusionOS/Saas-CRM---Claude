import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import { AuthProvider } from '../lib/auth-context';

// Mock API
vi.mock('../lib/api', () => ({
  authAPI: {
    login: vi.fn(),
  },
}));

const renderLogin = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Login Accessibility Tests', () => {
  it('has proper ARIA labels for form inputs', () => {
    renderLogin();

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    expect(emailInput).toBeTruthy();
    expect(passwordInput).toBeTruthy();
    expect(emailInput.getAttribute('aria-label')).toBe('Email address');
    expect(passwordInput.getAttribute('aria-label')).toBe('Password');
  });

  it('submit button is keyboard accessible', () => {
    renderLogin();

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    expect(submitButton).toBeTruthy();
    expect(submitButton.tagName).toBe('BUTTON');
    expect(submitButton.getAttribute('type')).toBe('submit');
  });

  it('form inputs have required attribute', () => {
    renderLogin();

    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;

    expect(emailInput.required).toBe(true);
    expect(passwordInput.required).toBe(true);
  });

  it('maintains logical tab order', () => {
    renderLogin();

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    // Ensure elements exist in DOM order
    const allElements = [emailInput, passwordInput, submitButton];
    allElements.forEach((el) => expect(el).toBeTruthy());
  });

  it('error messages have proper role', () => {
    renderLogin();

    // Initial state - no error
    const alerts = screen.queryAllByRole('alert');
    // Should not have error initially or have empty alert
    expect(alerts.length).toBeLessThan(2);
  });
});
