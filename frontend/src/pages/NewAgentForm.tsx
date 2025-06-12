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
    } catch (err: any) {
      setMessage(err.message);
    }
  };

  return (
    <form onSubmit={submit} className="p-4 space-y-2">
      <h1 className="text-xl font-bold">New Agent</h1>
      <input
        className="border p-2 w-full"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Agent name"
      />
      <button className="bg-primary text-white px-4 py-2 rounded" type="submit">
        Create
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}
