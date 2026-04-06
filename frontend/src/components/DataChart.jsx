import React, { useState, useMemo, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { BarChart3, LineChart as LineIcon, PieChart as PieIcon } from 'lucide-react';

export default function DataChart({ data }) {
  const [chartType, setChartType] = useState('bar'); // 'bar', 'line', 'pie'
  const [selectedXAxis, setSelectedXAxis] = useState('');
  const [selectedYAxis, setSelectedYAxis] = useState('');

  // Analyze data to find numeric and categorical columns
  const analysis = useMemo(() => {
    if (!data || data.length === 0) return null;
    
    const sample = data[0];
    const columns = Object.keys(sample);
    
    let numericCols = [];
    let categoricalCols = [];
    
    for (const col of columns) {
      let isNumeric = true;
      for (let i = 0; i < Math.min(data.length, 5); i++) {
        const val = data[i][col];
        if (val !== null && val !== undefined && isNaN(Number(val))) {
          isNumeric = false;
          break;
        }
      }
      if (isNumeric) numericCols.push(col);
      else categoricalCols.push(col);
    }
    
    if (numericCols.length === 0) return null; // Can't chart without numbers
    
    const defaultX = categoricalCols.length > 0 ? categoricalCols[0] : columns[0];
    const yAxisCols = numericCols.filter(c => !c.toLowerCase().includes('id'));
    const defaultY = yAxisCols.length > 0 ? yAxisCols[0] : numericCols[0];
    
    return { columns, numericCols, categoricalCols, defaultX, defaultY };
  }, [data]);

  useEffect(() => {
    if (analysis) {
      setSelectedXAxis(analysis.defaultX);
      setSelectedYAxis(analysis.defaultY);
    }
  }, [analysis]);

  if (!analysis || !selectedXAxis || !selectedYAxis) return null;

  const { columns, numericCols } = analysis;
  
  const chartData = data.map(row => ({
    ...row,
    [selectedYAxis]: Number(row[selectedYAxis]),
    [selectedXAxis]: String(row[selectedXAxis])
  }));

  const COLORS = ['#10a37f', '#f3f4f6', '#9ca3af', '#4b5563', '#374151', '#1f2937'];

  const renderChart = () => {
    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff" strokeOpacity={0.05} />
              <XAxis dataKey={selectedXAxis} stroke="#6b7280" tick={{ fill: '#e5e7eb', fontSize: 13 }} tickMargin={8} angle={-15} textAnchor="end" />
              <YAxis stroke="#6b7280" tick={{ fill: '#e5e7eb', fontSize: 13 }} tickMargin={8} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#171717', border: '1px solid rgba(255,255,255,0.1)', color: '#f3f4f6', borderRadius: '8px', fontSize: '14px' }} 
                itemStyle={{ color: '#10a37f', fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '14px', color: '#e5e7eb' }} />
              <Line type="monotone" dataKey={selectedYAxis} stroke="#10a37f" strokeWidth={3} dot={{ r: 4, fill: '#10a37f', strokeWidth: 0 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={{ stroke: '#9ca3af', strokeWidth: 1 }}
                outerRadius={100}
                fill="#10a37f"
                dataKey={selectedYAxis}
                nameKey={selectedXAxis}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#171717', border: '1px solid rgba(255,255,255,0.1)', color: '#f3f4f6', borderRadius: '8px', fontSize: '14px' }} 
                itemStyle={{ color: '#f3f4f6', fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '14px', color: '#e5e7eb' }} />
            </PieChart>
          </ResponsiveContainer>
        );
      case 'bar':
      default:
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff" strokeOpacity={0.05} />
              <XAxis dataKey={selectedXAxis} stroke="#6b7280" tick={{ fill: '#e5e7eb', fontSize: 13 }} tickMargin={8} angle={-15} textAnchor="end" />
              <YAxis stroke="#6b7280" tick={{ fill: '#e5e7eb', fontSize: 13 }} tickMargin={8} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#171717', border: '1px solid rgba(255,255,255,0.1)', color: '#f3f4f6', borderRadius: '8px', fontSize: '14px' }} 
                itemStyle={{ color: '#10a37f', fontWeight: 'bold' }}
                cursor={{ fill: '#ffffff', opacity: 0.05 }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '14px', color: '#e5e7eb' }} />
              <Bar dataKey={selectedYAxis} fill="#10a37f" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <div className="mt-2 border border-white/10 bg-[#171717] rounded-xl overflow-hidden">
      <div className="flex flex-wrap gap-3 justify-between items-center bg-[#212121]/50 px-4 py-2.5 border-b border-white/10">
        <div className="flex items-center gap-3 text-sm text-gray-300">
          <div className="flex items-center gap-2 text-xs">
            <label className="font-semibold text-gray-400">Y-Axis:</label>
            <select 
              value={selectedYAxis} 
              onChange={(e) => setSelectedYAxis(e.target.value)}
              className="bg-[#2a2a2a] border border-transparent rounded px-2 py-1 text-white outline-none focus:border-white/20 transition-colors"
            >
              {numericCols.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>
          <span className="text-gray-600 text-xs">by</span>
          <div className="flex items-center gap-2 text-xs">
            <label className="font-semibold text-gray-400">X-Axis:</label>
            <select 
              value={selectedXAxis} 
              onChange={(e) => setSelectedXAxis(e.target.value)}
              className="bg-[#2a2a2a] border border-transparent rounded px-2 py-1 text-white outline-none focus:border-white/20 transition-colors"
            >
              {columns.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex bg-[#2a2a2a] rounded-lg p-0.5 border border-white/5">
          <button 
            onClick={() => setChartType('bar')}
            className={`p-1.5 rounded-md transition-colors ${chartType === 'bar' ? 'bg-[#3f3f3f] text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
            title="Bar Chart"
          >
            <BarChart3 className="w-3.5 h-3.5" />
          </button>
          <button 
            onClick={() => setChartType('line')}
            className={`p-1.5 rounded-md transition-colors ${chartType === 'line' ? 'bg-[#3f3f3f] text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
            title="Line Chart"
          >
            <LineIcon className="w-3.5 h-3.5" />
          </button>
          <button 
            onClick={() => setChartType('pie')}
            className={`p-1.5 rounded-md transition-colors ${chartType === 'pie' ? 'bg-[#3f3f3f] text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
            title="Pie Chart"
          >
            <PieIcon className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
      <div className="p-4" style={{ height: '350px' }}>
        {renderChart()}
      </div>
    </div>
  );
}
