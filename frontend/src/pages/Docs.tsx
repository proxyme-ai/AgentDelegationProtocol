import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Docs() {
  const [md, setMd] = useState('');

  useEffect(() => {
    fetch('/docs.md').then(r => r.text()).then(setMd);
  }, []);

  return (
    <div className="p-4">
      <div className="prose card bg-base-100 shadow p-4">
        <ReactMarkdown>{md}</ReactMarkdown>
      </div>
    </div>
  );
}
