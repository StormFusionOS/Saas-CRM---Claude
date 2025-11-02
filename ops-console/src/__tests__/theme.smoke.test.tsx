import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';

describe('Theme Smoke Tests', () => {
  it('Button renders with primary variant classes', () => {
    render(<Button variant="primary">Click me</Button>);
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeTruthy();
    expect(button.className).toContain('bg-primary');
  });

  it('Button has visible focus ring', () => {
    render(<Button variant="primary">Focus test</Button>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('focus-ring');
  });

  it('Card renders with default variant', () => {
    render(<Card>Card content</Card>);
    const card = screen.getByText(/card content/i);
    expect(card.parentElement?.className).toContain('bg-bg-elev');
  });

  it('Card renders with glass variant', () => {
    render(<Card variant="glass">Glass card</Card>);
    const card = screen.getByText(/glass card/i);
    expect(card.parentElement?.className).toContain('glass-surface');
  });

  it('Input renders with label and focus styles', () => {
    render(<Input label="Test Input" id="test" />);
    const input = screen.getByLabelText(/test input/i);
    const inputElement = input as HTMLInputElement;
    expect(inputElement).toBeTruthy();
    expect(inputElement.className).toContain('focus-ring');
    expect(inputElement.className).toContain('bg-bg-elev');
  });

  it('Input shows error state', () => {
    render(<Input label="Email" id="email" error="Invalid email" />);
    const errorText = screen.getByText(/invalid email/i);
    expect(errorText).toBeTruthy();
    expect(errorText.className).toContain('text-error');
  });
});
