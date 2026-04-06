import React, { useState, useEffect, useRef } from 'react';
import { ArrowUp, Check } from 'lucide-react';
import { getDatabaseSchema } from '../services/api';

export default function ChatInput({ onSendMessage, isLoading }) {
  const [input, setInput] = useState('');
  const [availableTables, setAvailableTables] = useState([]);
  const [selectedTables, setSelectedTables] = useState(['All Tables']); // 'All Tables', or list of explicit tables
  const textareaRef = useRef(null);

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

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [input]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const tablesToPass = selectedTables.includes('All Tables') ? [] : selectedTables;
    onSendMessage(input.trim(), tablesToPass);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleTableSelection = (table) => {
    if (table === 'All Tables') {
      setSelectedTables([table]);
      return;
    }

    let newSelection = selectedTables.filter(t => t !== 'All Tables');
    if (newSelection.includes(table)) {
      newSelection = newSelection.filter(t => t !== table);
      if (newSelection.length === 0) newSelection = ['All Tables'];
    } else {
      newSelection.push(table);
    }
    setSelectedTables(newSelection);
  };

  const allOptions = ['All Tables', ...availableTables];

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col gap-2 relative">
      <form 
        onSubmit={handleSubmit}
        className="relative flex flex-col w-full rounded-3xl bg-[#2f2f2f] shadow-[0_0_15px_rgba(0,0,0,0.2)] focus-within:ring-1 focus-within:ring-white/20 transition-all p-2 pl-4 border border-white/5"
      >
        <textarea
          ref={textareaRef}
          rows={1}
          placeholder="Message Text-to-SQL Assistant..."
          className="w-full max-h-[200px] bg-transparent outline-none text-gray-100 placeholder-gray-400 resize-none py-2 pr-12 leading-relaxed"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          style={{ minHeight: '44px' }}
        />
        
        {/* Submit Button */}
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="absolute right-3 bottom-3 p-1.5 bg-gray-100 hover:bg-white text-black rounded-full disabled:opacity-30 disabled:bg-[#2f2f2f] disabled:text-gray-500 disabled:border disabled:border-white/10 transition-colors"
        >
          <ArrowUp className="w-5 h-5" strokeWidth={2.5} />
        </button>

        {/* Minimal Context Selector */}
        <div className="flex flex-wrap gap-1.5 pt-2 pb-1 pr-12 mt-1 border-t border-white/5">
          <span className="text-[10px] text-gray-500 self-center mr-1 uppercase tracking-wider font-semibold">Context:</span>
          {allOptions.map(option => {
            const isSelected = selectedTables.includes(option);
            return (
              <button
                key={option}
                type="button"
                onClick={() => toggleTableSelection(option)}
                className={`flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium rounded-md transition-colors border ${
                  isSelected 
                    ? 'bg-white/10 text-gray-200 border-transparent' 
                    : 'bg-transparent text-gray-500 border-white/5 hover:bg-white/5 hover:text-gray-300'
                }`}
              >
                {isSelected && <Check className="w-3 h-3" />}
                {option}
              </button>
            )
          })}
        </div>
      </form>
    </div>
  );
}
