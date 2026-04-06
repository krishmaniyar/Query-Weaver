import React from 'react';
import { TableProperties } from 'lucide-react';

export default function ResultTable({ result }) {
  if (!result || !Array.isArray(result) || result.length === 0) {
    return (
      <div className="p-4 bg-[#171717] rounded-xl border border-white/5 text-gray-400 text-sm mt-2">
        No results found for this query.
      </div>
    );
  }

  const columns = Object.keys(result[0] || {});

  return (
    <div className="mt-2 overflow-hidden rounded-xl border border-white/10 w-full bg-[#171717]">
      <div className="flex items-center gap-2 bg-[#212121]/50 px-4 py-2.5 border-b border-white/10">
        <TableProperties className="w-4 h-4 text-gray-400" />
        <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
          Query Results ({result.length} rows)
        </span>
      </div>
      <div className="overflow-auto max-h-96 relative custom-scrollbar">
        <table className="w-full text-left text-sm text-gray-300 whitespace-nowrap">
          <thead className="bg-[#171717] text-xs uppercase text-gray-400 sticky top-0 shadow-sm">
            <tr>
              {columns.map((col, idx) => (
                <th key={idx} scope="col" className="px-4 py-3 font-semibold tracking-wider border-b border-white/10">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {result.map((row, rowIdx) => (
              <tr 
                key={rowIdx} 
                className={`hover:bg-white/5 transition-colors ${
                  rowIdx % 2 === 0 ? 'bg-white/[0.02]' : 'bg-transparent'
                }`}
              >
                {columns.map((col, colIdx) => {
                  let cellValue = row[col];
                  if (typeof cellValue === 'object' && cellValue !== null) {
                    cellValue = JSON.stringify(cellValue);
                  }
                  
                  return (
                    <td 
                      key={colIdx} 
                      className="px-4 py-3 border-r border-white/5 last:border-0 truncate max-w-[250px]" 
                      title={typeof cellValue === 'string' ? cellValue : ''}
                    >
                      {cellValue !== null && cellValue !== undefined ? String(cellValue) : <span className="text-gray-500 italic">null</span>}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
