import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import NewAgentForm from './pages/NewAgentForm';
import DelegationsList from './pages/DelegationsList';
import Docs from './pages/Docs';

export default function App() {
  return (
    <BrowserRouter>
      <nav className="p-4 bg-gray-100 flex space-x-4">
        <Link to="/">Dashboard</Link>
        <Link to="/new-agent">New Agent</Link>
        <Link to="/delegations">Delegations</Link>
        <Link to="/docs">Docs</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/new-agent" element={<NewAgentForm />} />
        <Route path="/delegations" element={<DelegationsList />} />
        <Route path="/docs" element={<Docs />} />
      </Routes>
    </BrowserRouter>
  );
}
