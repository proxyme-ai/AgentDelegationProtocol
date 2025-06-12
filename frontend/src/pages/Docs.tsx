import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Docs() {
  const [md, setMd] = useState('');

  useEffect(() => {
    fetch('/docs.md').then(r => r.text()).then(setMd);
  }, []);

  return (
    <div className="prose p-4">
      <ReactMarkdown>{md}</ReactMarkdown>
    </div>
  );
}
