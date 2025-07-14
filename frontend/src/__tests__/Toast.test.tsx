import { vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ToastContainer, useToast } from '../components/Toast';

function TestComponent() {
  const toast = useToast();

  return (
    <div>
      <button onClick={() => toast.success('Success', 'Test success message')}>
        Success Toast
      </button>
      <button onClick={() => toast.error('Error', 'Test error message')}>
        Error Toast
      </button>
      <ToastContainer messages={toast.messages} onClose={toast.removeToast} />
    </div>
  );
}

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('displays success toast message', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<TestComponent />);

    const successButton = screen.getByText('Success Toast');
    await user.click(successButton);

    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.getByText('Test success message')).toBeInTheDocument();
    expect(screen.getByText('✅')).toBeInTheDocument();
  });

  it('displays error toast message', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<TestComponent />);

    const errorButton = screen.getByText('Error Toast');
    await user.click(errorButton);

    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
    expect(screen.getByText('❌')).toBeInTheDocument();
  });

  it('removes toast after timeout', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<TestComponent />);

    const successButton = screen.getByText('Success Toast');
    await user.click(successButton);

    expect(screen.getByText('Success')).toBeInTheDocument();

    // Fast forward time to trigger auto-removal
    vi.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.queryByText('Success')).not.toBeInTheDocument();
    });
  });

  it('removes toast when close button is clicked', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<TestComponent />);

    const successButton = screen.getByText('Success Toast');
    await user.click(successButton);

    expect(screen.getByText('Success')).toBeInTheDocument();

    const closeButton = screen.getByText('✕');
    await user.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('Success')).not.toBeInTheDocument();
    });
  });
});