import { render, screen } from '@testing-library/react';
import Icon from './Icon';

describe('Icon', () => {
  it('renders the icon name as text content', () => {
    render(<Icon name="dashboard" />);
    expect(screen.getByText('dashboard')).toBeInTheDocument();
  });

  it('applies material-symbols-outlined class', () => {
    render(<Icon name="settings" />);
    const el = screen.getByText('settings');
    expect(el).toHaveClass('material-symbols-outlined');
  });

  it('uses default size of 24', () => {
    render(<Icon name="home" />);
    const el = screen.getByText('home');
    expect(el.style.fontSize).toBe('24px');
  });

  it('accepts custom size', () => {
    render(<Icon name="home" size={32} />);
    const el = screen.getByText('home');
    expect(el.style.fontSize).toBe('32px');
  });

  it('renders unfilled by default', () => {
    render(<Icon name="star" />);
    const el = screen.getByText('star');
    expect(el.style.fontVariationSettings).toContain("'FILL' 0");
  });

  it('renders filled when prop is true', () => {
    render(<Icon name="star" filled />);
    const el = screen.getByText('star');
    expect(el.style.fontVariationSettings).toContain("'FILL' 1");
  });

  it('appends custom className', () => {
    render(<Icon name="search" className="text-primary" />);
    const el = screen.getByText('search');
    expect(el).toHaveClass('material-symbols-outlined');
    expect(el).toHaveClass('text-primary');
  });

  it('has aria-hidden for accessibility', () => {
    render(<Icon name="menu" />);
    const el = screen.getByText('menu');
    expect(el).toHaveAttribute('aria-hidden', 'true');
  });
});
