import React, { useState, useEffect } from 'react';
import { SendHorizonal, Check } from 'lucide-react';
import { getDatabaseSchema } from '../services/api';

export default function ChatInput({ onSendMessage, isLoading }) {
  const [input, setInput] = useState('');
  const [availableTables, setAvailableTables] = useState([]);
  const [selectedTables, setSelectedTables] = useState(['Auto']); // 'Auto', 'All Tables', or list of explicit tables

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const schema = await getDatabaseSchema();
        if (Array.isArray(schema)) {
          setAvailableTables(schema.map(t => t.table));
        }
      } catch (err) {
        console.error("Failed to fetch tables for selection", err);
      }
    };
    
    // Initial fetch
    fetchTables();

    // Listen for schema changes from backend
    const SSE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/schema/events';
    const es = new EventSource(SSE_URL);
    
    es.addEventListener('schema_changed', () => {
      fetchTables();
    });

    es.onerror = () => {
      console.warn('SSE connection lost in ChatInput, will reconnect automatically.');
    };

    return () => es.close();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    // Pass 'Auto' as empty array for backend defaulting, else pass the literal selections
    const tablesToPass = selectedTables.includes('Auto') ? [] : selectedTables;
    onSendMessage(input.trim(), tablesToPass);
    setInput('');
  };

  const toggleTableSelection = (table) => {
    if (table === 'Auto' || table === 'All Tables') {
      setSelectedTables([table]);
      return;
    }

    // Toggle specific table
    let newSelection = selectedTables.filter(t => t !== 'Auto' && t !== 'All Tables');
    if (newSelection.includes(table)) {
      newSelection = newSelection.filter(t => t !== table);
      if (newSelection.length === 0) newSelection = ['Auto'];
    } else {
      newSelection.push(table);
    }
    setSelectedTables(newSelection);
  };

  const allOptions = ['Auto', 'All Tables', ...availableTables];

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col gap-2">
      {/* Table Selector Pills */}
      <div className="flex flex-wrap gap-2 px-2">
        <span className="text-xs text-gray-400 self-center mr-1 tracking-wide uppercase">Context:</span>
        {allOptions.map(option => {
          const isSelected = selectedTables.includes(option);
          return (
            <button
              key={option}
              type="button"
              onClick={() => toggleTableSelection(option)}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-full transition-all border ${
                isSelected 
                  ? 'bg-blue-600/20 text-blue-400 border-blue-500/50' 
                  : 'bg-[#2a2a2a] text-gray-400 border-white/5 hover:border-white/20 hover:text-gray-200'
              }`}
            >
              {isSelected && <Check className="w-3 h-3" />}
              {option}
            </button>
          )
        })}
      </div>

      <form 
        onSubmit={handleSubmit}
        className="relative flex items-center w-full rounded-3xl bg-[#2f2f2f] border border-white/10 shadow-lg focus-within:ring-1 focus-within:ring-white/20 transition-all p-1.5"
      >
        <input
          type="text"
          placeholder="Message Text-to-SQL Assistant..."
          className="w-full bg-transparent px-4 py-2 outline-none text-gray-100 placeholder-gray-400"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="absolute right-2 p-2 bg-gray-200 hover:bg-white text-[#212121] rounded-full disabled:opacity-30 disabled:bg-gray-600 disabled:text-gray-400 transition-colors"
        >
          <SendHorizonal className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
}
