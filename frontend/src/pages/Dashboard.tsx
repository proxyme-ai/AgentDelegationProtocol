import { useEffect, useState } from 'react';
import { getDelegations } from '../services/api';
import type { Delegation } from '../types.ts';

export default function Dashboard() {
  const [delegations, setDelegations] = useState<Delegation[]>([]);

  useEffect(() => {
    getDelegations().then(setDelegations).catch(() => setDelegations([]));
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <h2 className="font-semibold mb-2">Pending Delegations</h2>
      <ul className="list-disc pl-4">
        {delegations.map((d) => (
          <li key={d.id}>{d.agent} - {d.status}</li>
        ))}
      </ul>
    </div>
  );
}
