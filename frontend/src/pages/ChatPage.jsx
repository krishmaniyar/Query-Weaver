import React, { useState, useEffect, useRef } from 'react';
import { Menu } from 'lucide-react';
import ChatInput from '../components/ChatInput';
import ChatMessage from '../components/ChatMessage';
import SQLViewer from '../components/SQLViewer';
import ResultTable from '../components/ResultTable';
import DataChart from '../components/DataChart';
import SchemaExplorer from '../components/SchemaExplorer';
import Loader from '../components/Loader';

import { sendQuery, executeConfirmedQuery } from '../services/api';

export default function ChatPage() {
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('chatHistory');
    return saved ? JSON.parse(saved) : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  const messagesEndRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const [isNearBottom, setIsNearBottom] = useState(true);

  // Intelligent scroll tracking
  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    // Considered "near bottom" if within 150px of the bottom
    setIsNearBottom(scrollHeight - scrollTop - clientHeight < 150);
  };

  const scrollToBottom = (force = false) => {
    if (force || isNearBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Scroll to bottom on initial load
  useEffect(() => {
    setTimeout(() => scrollToBottom(true), 100);
  }, []);

  // When messages update, only scroll if they were already near bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // When loading starts (user sends command), forcefully scroll down
  useEffect(() => {
    if (isLoading) {
      scrollToBottom(true);
    }
  }, [isLoading]);

  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(messages));
  }, [messages]);

  const handleSendMessage = async (text, selectedTables) => {
    // 1. Immediately append the user message in a pending state
    setMessages(prev => [...prev, {
      question: text,
      isPending: true,
      timestamp: new Date().toISOString()
    }]);
    setIsLoading(true);

    try {
      const response = await sendQuery(text, selectedTables);
      
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        newMessages[lastIndex] = {
          ...newMessages[lastIndex],
          isPending: false,
          sql: response.sql,
          result: response.result || response.results,
          needsConfirmation: response.requires_confirmation,
        };
        return newMessages;
      });
    } catch (error) {
      let errorMessage = error.response?.data?.detail || error.message;
      if (typeof errorMessage === 'object' && errorMessage !== null) {
        errorMessage = errorMessage.message || errorMessage.error || JSON.stringify(errorMessage);
      }
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        newMessages[lastIndex] = {
          ...newMessages[lastIndex],
          isPending: false,
          isError: true,
          errorMessage: String(errorMessage),
        };
        return newMessages;
      });
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmQuery = async (index, question, sql) => {
    setMessages(prev => {
      const newMessages = [...prev];
      newMessages[index] = { ...newMessages[index], isPending: true };
      return newMessages;
    });
    setIsLoading(true);

    try {
      const response = await executeConfirmedQuery(question, sql);
      
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[index] = {
          ...newMessages[index],
          isPending: false,
          sql: response.sql,
          result: response.result || response.results,
          needsConfirmation: false,
        };
        return newMessages;
      });
    } catch (error) {
      let errorMessage = error.response?.data?.detail || error.message;
      if (typeof errorMessage === 'object' && errorMessage !== null) {
        errorMessage = errorMessage.message || errorMessage.error || JSON.stringify(errorMessage);
      }
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[index] = {
          ...newMessages[index],
          isPending: false,
          isError: true,
          errorMessage: String(errorMessage),
          needsConfirmation: false,
        };
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#212121] text-gray-100 selection:bg-gray-700">
      <SchemaExplorer isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
      
      {!isSidebarOpen && (
        <div className="absolute top-4 left-4 z-10">
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 text-gray-400 hover:bg-[#2f2f2f] hover:text-white rounded-lg transition-colors border border-transparent hover:border-white/10"
            title="Open Schema Explorer"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>
      )}

      <div className="flex-1 flex flex-col h-full relative overflow-hidden">
        {/* Main Scrolling Area */}
        <div 
          ref={scrollContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto w-full flex flex-col items-center pb-32 scroll-smooth"
        >
          {messages.length === 0 && !isLoading ? (
            <div className="flex-1 w-full max-w-3xl flex flex-col items-center justify-center px-4 mt-32 mb-auto">
              <h1 className="text-4xl font-semibold text-gray-100 tracking-tight mb-4">
                Text-to-SQL Assistant
              </h1>
              <p className="text-gray-400 text-base text-center max-w-md">
                Ask natural language questions to query, visualize, and analyze your database seamlessly.
              </p>
            </div>
          ) : (
            <div className="w-full h-8 flex-shrink-0" /> /* Top padding block */
          )}
          
          <main className="flex-1 w-full max-w-3xl px-4 flex flex-col">
            {messages.map((msg, index) => (
              <div key={index} className="animate-in fade-in slide-in-from-bottom-2 duration-200 ease-out flex flex-col mb-8">
                <ChatMessage message={{ role: 'user', content: msg.question }} />
                
                {!msg.isPending && (
                  <div className="">
                    {msg.isError ? (
                      <>
                        <ChatMessage message={{ role: 'assistant', content: 'Sorry, an error occurred while executing that query.' }} />
                        <div className="ml-12 max-w-[85%] mt-2 p-3 bg-red-900/20 border border-red-800/50 rounded-lg text-red-400 text-sm whitespace-pre-wrap">
                          {msg.errorMessage}
                        </div>
                      </>
                    ) : msg.needsConfirmation ? (
                      <>
                        <ChatMessage message={{ role: 'assistant', content: 'This query modifies data. Please review and confirm to execute:' }} />
                        <div className="ml-12 max-w-full mt-4 flex flex-col gap-6">
                           <SQLViewer sql={msg.sql} />
                           <div className="flex gap-4">
                              <button 
                                 onClick={() => handleConfirmQuery(index, msg.question, msg.sql)} 
                                 className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
                                 disabled={isLoading}
                              >
                                 Run Query
                              </button>
                           </div>
                        </div>
                      </>
                    ) : (
                      <>
                        <ChatMessage message={{ role: 'assistant', content: 'Here is the SQL query and result:' }} />
                        <div className="ml-12 max-w-full mt-4 flex flex-col gap-6">
                          <SQLViewer sql={msg.sql} />
                          <ResultTable result={msg.result} />
                          <DataChart data={msg.result} />
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="animate-in fade-in slide-in-from-bottom-2 duration-200 ease-out flex flex-col mb-8">
                 <div>
                    <ChatMessage message={{ role: 'assistant', content: '' }} />
                    <div className="ml-12 -mt-4">
                      <Loader text="Thinking..." />
                    </div>
                 </div>
              </div>
            )}
            
            {/* Scroll Anchor */}
            <div ref={messagesEndRef} className="h-32 flex-shrink-0" />
          </main>
        </div>

        {/* Sticky Input Footer & Gradient Mask */}
        <div className="w-full absolute bottom-0 flex flex-col items-center bg-gradient-to-t from-[#212121] via-[#212121] to-transparent pt-12 pb-6 px-4 pointer-events-none">
           <div className="w-full max-w-3xl pointer-events-auto">
             <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
             <div className="text-center text-xs text-gray-500 mt-3 font-medium">
                SQL Assistant can make mistakes. Consider verifying important data.
             </div>
           </div>
        </div>
      </div>
    </div>
  );
}
