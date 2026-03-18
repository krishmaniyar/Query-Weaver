import React from 'react';
import { Database, User } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex items-start gap-4 mb-6 ${isUser ? 'flex-row-reverse' : ''}`}>
      {!isUser && (
        <div className="p-1.5 rounded-full flex-shrink-0 bg-white border border-gray-600">
          <Database className="w-5 h-5 text-black" />
        </div>
      )}
      
      <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div 
          className={`px-5 py-3 ${
            isUser 
              ? 'bg-[#2f2f2f] text-gray-100 rounded-3xl' 
              : 'text-gray-100 bg-transparent px-0 py-1'
          }`}
        >
          {message.content}
        </div>
      </div>
    </div>
  );
}
