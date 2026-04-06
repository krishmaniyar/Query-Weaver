import React from 'react';
import { Database } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  // User Message (Right aligned padded bubble)
  if (isUser) {
    return (
      <div className="flex w-full justify-end mb-2">
        <div className="bg-[#2f2f2f] text-gray-100 px-5 py-3 rounded-2xl rounded-tr-sm max-w-[80%] whitespace-pre-wrap leading-relaxed">
          {message.content}
        </div>
      </div>
    );
  }

  // Assistant Message (Left aligned with icon)
  return (
    <div className="flex items-start gap-4 mb-2 w-full">
      <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center bg-white/10 border border-white/5 mt-0.5">
        <Database className="w-4 h-4 text-gray-200" />
      </div>
      
      <div className="flex flex-col flex-1 min-w-0 pt-1">
        {/* We can hide 'Assistant' name to make it perfectly ChatGPT like, but retaining for clarity */}
        <div className="text-gray-200 leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    </div>
  );
}
