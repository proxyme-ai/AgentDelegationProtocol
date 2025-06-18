import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Navbar from '../components/Navbar';

describe('Navbar', () => {
  it('renders navigation links', () => {
    render(<BrowserRouter><Navbar /></BrowserRouter>);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('New Agent')).toBeInTheDocument();
    expect(screen.getByText('Delegations')).toBeInTheDocument();
    expect(screen.getByText('Docs')).toBeInTheDocument();
  });
});
