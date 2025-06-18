import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <div className="navbar bg-base-100 shadow mb-4">
      <div className="flex-1">
        <Link to="/" className="btn btn-ghost text-xl">Agent Dashboard</Link>
      </div>
      <div className="flex-none">
        <ul className="menu menu-horizontal px-1">
          <li><Link to="/">Dashboard</Link></li>
          <li><Link to="/new-agent">New Agent</Link></li>
          <li><Link to="/delegations">Delegations</Link></li>
          <li><Link to="/docs">Docs</Link></li>
        </ul>
      </div>
    </div>
  );
}
