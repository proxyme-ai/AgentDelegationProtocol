import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import NewAgentForm from './pages/NewAgentForm';
import DelegationsList from './pages/DelegationsList';
import Docs from './pages/Docs';
import Navbar from './components/Navbar';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/new-agent" element={<NewAgentForm />} />
        <Route path="/delegations" element={<DelegationsList />} />
        <Route path="/docs" element={<Docs />} />
      </Routes>
    </BrowserRouter>
  );
}
