import { useState } from 'react';
import { createAgent } from '../services/api';

export default function NewAgentForm() {
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return setMessage('Name required');
    try {
      await createAgent({ name });
      setMessage('Agent created');
      setName('');
    } catch (err: unknown) {
      setMessage(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <form onSubmit={submit} className="p-4 space-y-2">
      <h1 className="text-xl font-bold">New Agent</h1>
      <input
        className="input input-bordered w-full"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Agent name"
      />
      <button className="btn btn-primary" type="submit">
        Create
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}
