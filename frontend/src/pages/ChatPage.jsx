import React, { useState, useEffect, useRef } from 'react';
import { Menu } from 'lucide-react';
import ChatInput from '../components/ChatInput';
import ChatMessage from '../components/ChatMessage';
import SQLViewer from '../components/SQLViewer';
import ResultTable from '../components/ResultTable';
import DataChart from '../components/DataChart';
import SchemaExplorer from '../components/SchemaExplorer';
import Loader from '../components/Loader';

import { sendQuery } from '../services/api';

export default function ChatPage() {
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('chatHistory');
    return saved ? JSON.parse(saved) : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(messages));
  }, [messages]);

  const handleSendMessage = async (text, selectedTables) => {
    setIsLoading(true);

    try {
      const response = await sendQuery(text, selectedTables);
      
      const newResponse = {
        question: text,
        sql: response.sql,
        result: response.result || response.results,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, newResponse]);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      setMessages(prev => [...prev, {
        question: text,
        isError: true,
        errorMessage: String(errorMessage),
        timestamp: new Date().toISOString()
      }]);
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#212121]">
      <SchemaExplorer isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
      
      {!isSidebarOpen && (
        <div className="absolute top-4 left-4 z-10">
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 text-gray-400 hover:bg-[#2f2f2f] hover:text-white rounded-lg transition-colors border border-white/10 bg-[#171717]"
            title="Open Schema Explorer"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>
      )}

      <div className="flex-1 flex flex-col h-full items-center p-4 overflow-hidden relative">
        <div className="w-full h-full flex flex-col max-w-4xl overflow-hidden">
          <header className="mb-4 text-center relative flex items-center justify-center">
            <div>
              <h1 className="text-3xl font-semibold text-gray-100 tracking-tight">
                Text-to-SQL Assistant
              </h1>
              <p className="text-gray-400 mt-2 text-sm">Ask natural language questions to query your database</p>
            </div>
          </header>
          
          <main className="flex-1 overflow-y-auto pr-2 px-4 py-4 flex flex-col gap-6 w-full">
            {messages.length === 0 && !isLoading && (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                Send a message to get started.
              </div>
            )}
            
            {messages.map((msg, index) => (
              <div key={index} className="animate-in fade-in slide-in-from-bottom-4 duration-500 flex flex-col gap-6">
                <ChatMessage message={{ role: 'user', content: msg.question }} />
                
                <div>
                  {msg.isError ? (
                    <>
                      <ChatMessage message={{ role: 'assistant', content: 'Sorry, an error occurred while executing that query.' }} />
                      <div className="ml-14 max-w-[85%] mt-2 p-3 bg-red-900/30 border border-red-800 rounded-lg text-red-400 text-sm">
                        {msg.errorMessage}
                      </div>
                    </>
                  ) : (
                    <>
                      <ChatMessage message={{ role: 'assistant', content: 'Here is the SQL query and result:' }} />
                      <div className="ml-14 max-w-[85%]">
                        <SQLViewer sql={msg.sql} />
                        <ResultTable result={msg.result} />
                        <DataChart data={msg.result} />
                      </div>
                    </>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="animate-in fade-in flex flex-col gap-6">
                 <div className="self-end mr-4">
                    <Loader text="Sending question..." />
                 </div>
                 <div className="ml-14 mt-2">
                    <Loader text="Generating SQL and executing query..." />
                 </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </main>

          <footer className="mt-6">
            <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
          </footer>
        </div>
      </div>
    </div>
  );
}
