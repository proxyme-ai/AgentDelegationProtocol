import { render, screen } from '@testing-library/react';
import { Loading, Skeleton, LoadingCard } from '../components/Loading';

describe('Loading', () => {
  it('renders loading spinner with default size', () => {
    render(<Loading />);
    
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('loading-spinner', 'loading-md');
  });

  it('renders loading spinner with custom size', () => {
    render(<Loading size="lg" />);
    
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('loading-spinner', 'loading-lg');
  });

  it('renders loading text when provided', () => {
    render(<Loading text="Loading data..." />);
    
    expect(screen.getByText('Loading data...')).toBeInTheDocument();
  });

  it('renders fullscreen loading when specified', () => {
    render(<Loading fullScreen />);
    
    const container = screen.getByRole('status').closest('div');
    expect(container).toHaveClass('fixed', 'inset-0');
  });
});

describe('Skeleton', () => {
  it('renders single skeleton line by default', () => {
    render(<Skeleton />);
    
    const skeletons = screen.getAllByRole('generic');
    expect(skeletons).toHaveLength(1);
  });

  it('renders multiple skeleton lines when specified', () => {
    render(<Skeleton lines={3} />);
    
    const skeletons = screen.getAllByRole('generic');
    expect(skeletons).toHaveLength(3);
  });

  it('applies custom className', () => {
    render(<Skeleton className="custom-class" />);
    
    const skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveClass('custom-class');
  });
});

describe('LoadingCard', () => {
  it('renders loading card with skeleton content', () => {
    render(<LoadingCard />);
    
    expect(screen.getByRole('generic')).toBeInTheDocument();
  });

  it('renders title skeleton when title is provided', () => {
    render(<LoadingCard title="Test Title" />);
    
    const skeletons = screen.getAllByRole('generic');
    expect(skeletons.length).toBeGreaterThan(1); // Title skeleton + content skeletons
  });

  it('renders specified number of content lines', () => {
    render(<LoadingCard lines={5} />);
    
    const skeletons = screen.getAllByRole('generic');
    expect(skeletons).toHaveLength(5);
  });
});