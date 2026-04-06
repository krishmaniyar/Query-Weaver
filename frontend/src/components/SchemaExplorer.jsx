import React, { useState, useEffect, useCallback } from 'react';
import { Database, TableProperties, ChevronRight, ChevronDown, Loader2, RefreshCw, Menu } from 'lucide-react';
import { getDatabaseSchema } from '../services/api';

const SSE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/schema/events';

export default function SchemaExplorer({ isOpen, onToggle }) {
  const [schema, setSchema] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedTables, setExpandedTables] = useState({});

  const fetchSchema = useCallback(async (showLoader = true) => {
    if (showLoader) setIsLoading(true);
    setError(null);
    try {
      const data = await getDatabaseSchema();
      setSchema(Array.isArray(data) ? data : []);

      if (Array.isArray(data)) {
        setExpandedTables(prev => {
          const next = {};
          data.forEach(t => {
            next[t.table] = t.table in prev ? prev[t.table] : true;
          });
          return next;
        });
      }
    } catch (err) {
      setError('Failed to load schema');
      console.error(err);
    } finally {
      if (showLoader) setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSchema();
  }, [fetchSchema]);

  useEffect(() => {
    const es = new EventSource(SSE_URL);
    es.addEventListener('schema_changed', () => {
      fetchSchema(false);
    });
    es.onerror = () => {
      console.warn('SSE connection lost, will reconnect automatically.');
    };
    return () => es.close();
  }, [fetchSchema]);

  const toggleTable = (tableName) => {
    setExpandedTables(prev => ({
      ...prev,
      [tableName]: !prev[tableName]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="w-64 bg-[#171717] flex flex-col h-full flex-shrink-0 transition-all duration-300 z-20">
      <div className="p-4 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-gray-300 font-semibold tracking-wide text-xs uppercase">
            <Database className="w-4 h-4" />
            <span>Schema</span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => fetchSchema()}
              disabled={isLoading}
              title="Refresh schema"
              className="p-1.5 rounded-lg hover:bg-white/5 text-gray-400 hover:text-gray-200 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onToggle}
              title="Close Schema Explorer"
              className="p-1.5 rounded-lg hover:bg-white/5 text-gray-400 hover:text-gray-200 transition-colors"
            >
              <Menu className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto px-2 pb-4">
        {isLoading ? (
          <div className="flex items-center justify-center p-4 text-gray-400">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="ml-2 text-sm">Loading...</span>
          </div>
        ) : error ? (
          <div className="text-red-400 text-sm p-2 text-center">{error}</div>
        ) : schema.length === 0 ? (
          <div className="text-gray-500 text-sm p-2 text-center">No tables found</div>
        ) : (
          <div className="space-y-1">
            {schema.map((tableInfo, idx) => (
              <div key={idx} className="mb-1">
                <button 
                  onClick={() => toggleTable(tableInfo.table)}
                  className="flex items-center w-full text-left px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors group"
                >
                  {expandedTables[tableInfo.table] ? (
                    <ChevronDown className="w-4 h-4 text-gray-500 mr-1.5" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-500 mr-1.5" />
                  )}
                  <TableProperties className="w-4 h-4 text-gray-400 mr-2 group-hover:text-gray-300 transition-colors" />
                  <span className="text-sm font-medium text-gray-300">{tableInfo.table}</span>
                </button>
                
                {expandedTables[tableInfo.table] && (
                  <ul className="pl-9 pr-2 py-1 space-y-1">
                    {tableInfo.columns?.map((col, colIdx) => (
                      <li key={colIdx} className="flex justify-between items-center text-xs">
                        <span className="text-gray-400 truncate pr-2" title={col.name}>{col.name}</span>
                        <span className="text-gray-500 font-mono text-[10px] uppercase">{col.type}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
