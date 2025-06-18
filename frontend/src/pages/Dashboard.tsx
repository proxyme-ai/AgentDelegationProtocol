import { useEffect, useState } from 'react';
import { getDelegations } from '../services/api';
import type { Delegation } from '../types.ts';

export default function Dashboard() {
  const [delegations, setDelegations] = useState<Delegation[]>([]);

  useEffect(() => {
    getDelegations().then(setDelegations).catch(() => setDelegations([]));
  }, []);

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <h2 className="font-semibold">Pending Delegations</h2>
      <div className="space-y-2">
        {delegations.map((d) => (
          <div key={d.id} className="card bg-base-100 shadow">
            <div className="card-body p-4 flex-row items-center justify-between">
              <span>{d.agent} - {d.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
