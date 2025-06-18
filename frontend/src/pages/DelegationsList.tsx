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
      <div className="space-y-2">
        {delegations.map((d) => (
          <div key={d.id} className="card bg-base-100 shadow">
            <div className="card-body p-4 flex-row items-center justify-between">
              <span>{d.agent}</span>
              <span className="space-x-2">
                <button className="btn btn-primary btn-sm" onClick={() => act(d.id, approveDelegation)}>Approve</button>
                <button className="btn btn-error btn-sm" onClick={() => act(d.id, denyDelegation)}>Deny</button>
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
