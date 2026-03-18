import React from 'react';
import { Loader2 } from 'lucide-react';

export default function Loader({ text = "Processing..." }) {
  return (
    <div className="flex items-center space-x-2 text-gray-400">
      <Loader2 className="w-5 h-5 animate-spin" />
      <span className="text-sm font-medium animate-pulse">{text}</span>
    </div>
  );
}
