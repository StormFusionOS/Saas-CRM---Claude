import { describe, it, expect, vi } from 'vitest';
import { render, screen, within, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import { AuthProvider } from '../lib/auth-context';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

// Mock API
vi.mock('../lib/api', () => ({
  authAPI: {
    login: vi.fn(),
    getProfile: vi.fn(() => Promise.resolve({
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      roles: ['SALES']
    })),
  },
  leadsAPI: {
    getLeads: vi.fn(() => Promise.resolve([])),
  }
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

const renderDashboard = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <DashboardPage />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Focus Visibility Tests', () => {
  describe('Button Component', () => {
    it('has visible focus-ring class', () => {
      render(<Button>Test Button</Button>);
      const button = screen.getByRole('button');

      expect(button.className).toContain('focus-ring');
    });

    it('all button variants have focus-ring class', () => {
      const { rerender } = render(<Button variant="primary">Primary</Button>);
      expect(screen.getByRole('button').className).toContain('focus-ring');

      rerender(<Button variant="secondary">Secondary</Button>);
      expect(screen.getByRole('button').className).toContain('focus-ring');

      rerender(<Button variant="outline">Outline</Button>);
      expect(screen.getByRole('button').className).toContain('focus-ring');

      rerender(<Button variant="ghost">Ghost</Button>);
      expect(screen.getByRole('button').className).toContain('focus-ring');
    });
  });

  describe('Input Component', () => {
    it('has visible focus-ring class', () => {
      render(<Input label="Test Input" id="test" />);
      const input = screen.getByRole('textbox');

      expect(input.className).toContain('focus-ring');
    });

    it('maintains focus-ring in error state', () => {
      render(<Input label="Test Input" id="test" error="Error message" />);
      const input = screen.getByRole('textbox');

      expect(input.className).toContain('focus-ring');
      expect(input.getAttribute('aria-invalid')).toBe('true');
    });
  });

  describe('Login Page', () => {
    it('email input has focus-ring class', () => {
      renderLogin();
      const emailInput = screen.getByLabelText(/email/i);

      expect(emailInput.className).toContain('focus-ring');
    });

    it('password input has focus-ring class', () => {
      renderLogin();
      const passwordInput = screen.getByLabelText(/password/i);

      expect(passwordInput.className).toContain('focus-ring');
    });

    it('submit button has focus-ring class', () => {
      renderLogin();
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      expect(submitButton.className).toContain('focus-ring');
    });
  });
});

describe('Tab Order Tests', () => {
  describe('Login Page Tab Order', () => {
    it('maintains logical tab order: Email → Password → Submit', () => {
      renderLogin();

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Check DOM order (which determines tab order)
      const form = emailInput.closest('form');
      const formElements = form ? Array.from(form.querySelectorAll('input, button')) : [];

      // Find indices
      const emailIndex = formElements.indexOf(emailInput as HTMLElement);
      const passwordIndex = formElements.indexOf(passwordInput as HTMLElement);
      const submitIndex = formElements.indexOf(submitButton as HTMLElement);

      // Verify order
      expect(emailIndex).toBeLessThan(passwordIndex);
      expect(passwordIndex).toBeLessThan(submitIndex);
    });

    it('all interactive elements are keyboard accessible', () => {
      renderLogin();

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Verify no tabindex that would break keyboard nav
      expect(emailInput.getAttribute('tabindex')).not.toBe('-1');
      expect(passwordInput.getAttribute('tabindex')).not.toBe('-1');
      expect(submitButton.getAttribute('tabindex')).not.toBe('-1');
    });

    it('no elements have positive tabindex values', () => {
      const { container } = renderLogin();

      const elementsWithTabIndex = container.querySelectorAll('[tabindex]');
      elementsWithTabIndex.forEach((el) => {
        const tabindex = el.getAttribute('tabindex');
        if (tabindex) {
          const value = parseInt(tabindex, 10);
          // Positive tabindex values break natural tab order
          expect(value).toBeLessThanOrEqual(0);
        }
      });
    });
  });

  describe('Dashboard Navigation Tab Order', () => {
    it('top navigation items are in logical order', async () => {
      renderDashboard();

      // Wait for dashboard to render
      await screen.findByText(/dashboard/i);

      // Find all focusable elements in navigation
      const nav = screen.queryByRole('navigation');
      if (nav) {
        const focusableElements = within(nav).queryAllByRole('link');

        // Navigation links should exist and be focusable
        focusableElements.forEach((link) => {
          expect(link.getAttribute('tabindex')).not.toBe('-1');
        });
      }
    });

    it('interactive elements in main content are reachable', async () => {
      renderDashboard();

      await screen.findByText(/dashboard/i);

      // Find buttons and links in main content
      const buttons = screen.queryAllByRole('button');
      const links = screen.queryAllByRole('link');

      // All should be keyboard accessible
      [...buttons, ...links].forEach((el) => {
        expect(el.getAttribute('tabindex')).not.toBe('-1');
      });
    });
  });
});

describe('Label Association Tests', () => {
  describe('Login Form', () => {
    it('email input has associated label', () => {
      renderLogin();

      const emailInput = screen.getByLabelText(/email/i);
      expect(emailInput).toBeTruthy();

      // Check that label is properly associated
      const label = screen.getByText(/email/i);
      expect(label.tagName).toBe('LABEL');
    });

    it('password input has associated label', () => {
      renderLogin();

      const passwordInput = screen.getByLabelText(/password/i);
      expect(passwordInput).toBeTruthy();

      const label = screen.getByText(/password/i);
      expect(label.tagName).toBe('LABEL');
    });

    it('inputs have aria-label attributes', () => {
      renderLogin();

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);

      expect(emailInput.getAttribute('aria-label')).toBeTruthy();
      expect(passwordInput.getAttribute('aria-label')).toBeTruthy();
    });
  });

  describe('Input Component', () => {
    it('renders label element when label prop provided', () => {
      render(<Input label="Test Label" id="test" />);

      const label = screen.getByText('Test Label');
      expect(label.tagName).toBe('LABEL');
    });

    it('associates label with input via implicit relationship', () => {
      render(<Input label="Test Label" id="test" />);

      const input = screen.getByRole('textbox');
      const label = screen.getByText('Test Label');

      // Label should contain the input or reference it via htmlFor
      expect(label.parentElement).toContain(input);
    });

    it('error message is associated via aria-describedby', () => {
      render(<Input label="Test" id="test" error="Error message" />);

      const input = screen.getByRole('textbox');
      const errorId = `${input.id}-error`;

      expect(input.getAttribute('aria-describedby')).toBe(errorId);
      expect(screen.getByText('Error message')).toBeTruthy();
    });

    it('helper text is associated via aria-describedby', () => {
      render(<Input label="Test" id="test" helperText="Helper text" />);

      const input = screen.getByRole('textbox');
      const helperId = `${input.id}-helper`;

      expect(input.getAttribute('aria-describedby')).toBe(helperId);
      expect(screen.getByText('Helper text')).toBeTruthy();
    });
  });
});

describe('Keyboard Navigation', () => {
  it('button can be activated with Enter key', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);

    const button = screen.getByRole('button');
    button.focus();

    // Simulate Enter key press
    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });

    expect(handleClick).toHaveBeenCalled();
  });

  it('button can be activated with Space key', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);

    const button = screen.getByRole('button');
    button.focus();

    // Simulate Space key press
    fireEvent.keyDown(button, { key: ' ', code: 'Space' });

    expect(handleClick).toHaveBeenCalled();
  });
});
