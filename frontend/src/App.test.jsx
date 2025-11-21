import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

vi.mock('react-chartjs-2', () => ({
  Line: () => <div data-testid="chart-mock" />,
}));

beforeEach(() => {
  // Evitar erros do html2canvas/file-saver durante os testes
  window.HTMLCanvasElement.prototype.getContext = vi.fn();
});

describe('App', () => {
  it('renderiza o título principal e ações importantes', () => {
    render(<App />);

    expect(screen.getByText('HospiCast - Previsão e Monitoramento Hospitalar')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '🔮 Previsão' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Monitoramento SUS/i })).toBeInTheDocument();
  });
});

