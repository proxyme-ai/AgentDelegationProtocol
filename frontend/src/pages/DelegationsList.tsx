import { useEffect, useState } from 'react';
import { getDelegations, approveDelegation, denyDelegation } from '../services/api';
import type { Delegation } from '../types.ts';

export default function DelegationsList() {
  const [delegations, setDelegations] = useState<Delegation[]>([]);

  const load = () => getDelegations().then(setDelegations);

  useEffect(() => { load(); }, []);

  const act = async (id: string, fn: (id: string) => Promise<Delegation>) => {
    await fn(id);
    await load();
  };

  return (
    <div className="p-4 space-y-2">
      <h1 className="text-xl font-bold">Delegations</h1>
      <ul className="space-y-2">
        {delegations.map((d) => (
          <li key={d.id} className="border p-2 flex justify-between">
            <span>{d.agent}</span>
            <span className="space-x-2">
              <button className="bg-primary text-white px-2" onClick={() => act(d.id, approveDelegation)}>Approve</button>
              <button className="bg-red-500 text-white px-2" onClick={() => act(d.id, denyDelegation)}>Deny</button>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
