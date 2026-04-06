import React, { useState } from 'react';
import { Terminal, Copy, Check } from 'lucide-react';

export default function SQLViewer({ sql }) {
  const [copied, setCopied] = useState(false);

  if (!sql) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-2 overflow-hidden rounded-xl border border-white/10 bg-[#171717] relative group">
      <div className="flex justify-between items-center bg-[#212121]/50 px-4 py-2 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-gray-400" />
          <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">Generated SQL</span>
        </div>
        <button
          onClick={handleCopy}
          className="p-1 rounded-md text-gray-400 hover:text-white hover:bg-white/10 transition"
          title="Copy SQL"
        >
          {copied ? <Check className="w-4 h-4 text-white" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
      <div className="p-4 overflow-x-auto custom-scrollbar">
        <pre className="text-sm font-mono text-gray-300 leading-relaxed">
          <code>{sql}</code>
        </pre>
      </div>
    </div>
  );
}
