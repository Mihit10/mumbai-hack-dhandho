import React, { useState, useEffect } from 'react';
import { TrendingUp, Zap, Brain, Bell, Calendar, Search, MessageSquare, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../services/api';

const Dashboard = ({ onBackToHome }) => {
  const [activeTab, setActiveTab] = useState('calendar');
  const [upcomingResults, setUpcomingResults] = useState([]);
  const [latestResults, setLatestResults] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([
    { type: 'bot', text: 'Hey! Ask me anything about recent results. Try: "How did Wipro perform?"' }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processingCompany, setProcessingCompany] = useState(null);
  const [notification, setNotification] = useState(null); // New state for toaster notification

  // Load data on mount and tab change
  useEffect(() => {
    if (activeTab === 'calendar') {
      loadUpcomingResults();
    } else if (activeTab === 'latest') {
      loadLatestResults();
    }
  }, [activeTab]);

  // Effect to clear notification after some time
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 3000); // Hide after 3 seconds
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const loadUpcomingResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.fetchUpcomingResults();
      setUpcomingResults(data);
    } catch (err) {
      setError('Failed to load upcoming results');
    } finally {
      setLoading(false);
    }
  };

  const loadLatestResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.fetchLatestResults();
      setLatestResults(data);
    } catch (err) {
      setError('Failed to load latest results');
    } finally {
      setLoading(false);
    }
  };

  const handleProcessResult = async (company, ticker) => {
    setProcessingCompany(company);
    const result = await api.triggerResultProcessing(company, ticker);
    
    if (result.status === 'success') {
      setNotification(`✅ Successfully processed ${company} results!`); // Set notification
      setActiveTab('latest'); // Switch to the 'latest' tab
    } else {
      setNotification(`❌ Error processing ${company}: ${result.error}`);
    }
    setProcessingCompany(null);
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    const userMessage = { type: 'user', text: chatInput };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    
    const thinkingMessage = { type: 'bot', text: '🤔 Analyzing...' };
    setChatMessages(prev => [...prev, thinkingMessage]);
    
    const answer = await api.sendChatMessage(userMessage.text);
    
    setChatMessages(prev => {
      const newMessages = prev.slice(0, -1);
      return [...newMessages, { type: 'bot', text: answer }];
    });
  };

  const renderTrendIndicator = (growth) => {
    if (growth === null || growth === undefined) return null;
    const isPositive = growth > 0;
    return (
      <span className={`flex items-center gap-1 text-sm font-semibold ${
        isPositive ? 'text-green-400' : 'text-red-400'
      }`}>
        {isPositive ? '↑' : '↓'} {Math.abs(growth).toFixed(1)}%
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Toaster Notification */}
      {notification && (
        <div className="fixed top-5 right-5 bg-gray-800 text-white p-4 rounded-lg shadow-lg z-50 animate-pulse">
          {notification}
        </div>
      )}

      {/* Header */}
      <nav className="border-b border-gray-800 bg-black/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
          <button 
            onClick={onBackToHome}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer group"
          >
            <Zap className="w-7 h-7 text-cyan-400 group-hover:scale-110 transition-transform" />
            <span className="text-2xl font-bold text-white">Khabri</span>
            <span className="ml-3 px-3 py-1 bg-green-500/20 text-green-400 text-xs font-semibold rounded-full animate-pulse">
              LIVE
            </span>
          </button>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input 
                type="text"
                placeholder="Search companies..."
                className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 focus:outline-none w-64"
              />
            </div>
            <button 
              onClick={activeTab === 'calendar' ? loadUpcomingResults : loadLatestResults}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className={`w-5 h-5 text-gray-400 hover:text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <Bell className="w-6 h-6 text-gray-400 hover:text-cyan-400 cursor-pointer transition-colors" />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-400">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
            <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-300">
              ✕
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-gray-800">
          {[
            { id: 'calendar', label: 'Results Calendar', icon: Calendar },
            { id: 'latest', label: 'Latest Results', icon: TrendingUp },
            { id: 'chat', label: 'Ask AI', icon: MessageSquare }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 font-semibold transition-all ${
                activeTab === tab.id
                  ? 'text-cyan-400 border-b-2 border-cyan-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Calendar Tab */}
        {activeTab === 'calendar' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                <Calendar className="w-8 h-8 text-cyan-400" />
                Upcoming Results
              </h2>
              <span className="text-gray-400">
                {upcomingResults.length} companies scheduled
              </span>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-20">
                <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
              </div>
            ) : upcomingResults.length === 0 ? (
              <div className="text-center py-20 text-gray-500">
                <Calendar className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>No upcoming results found. Backend might be starting up...</p>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                {upcomingResults.map((result, idx) => (
                  <div 
                    key={idx}
                    className="group p-5 bg-gray-800/50 border border-gray-700 rounded-xl hover:border-cyan-500/50 transition-all hover:scale-105 cursor-pointer"
                    onClick={() => handleProcessResult(result.company_name, result.company_symbol)}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-xl font-bold text-white">{result.company_name}</h3>
                        <p className="text-sm text-gray-500">{result.company_symbol}</p>
                      </div>
                      <span className="px-2 py-1 bg-cyan-500/20 text-cyan-400 text-xs rounded-full">
                        {result.sector || 'N/A'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-400 mb-3">
                      <Calendar className="w-4 h-4" />
                      <span className="text-sm">{result.result_date}</span>
                    </div>
                    {processingCompany === result.company_name ? (
                      <div className="flex items-center gap-2 text-cyan-400 text-sm">
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Processing...
                      </div>
                    ) : (
                      <div className="text-cyan-400 text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                        Click to process →
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Latest Results Tab */}
        {activeTab === 'latest' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                <Sparkles className="w-8 h-8 text-green-400" />
                Latest Analysis
              </h2>
              <span className="text-gray-400">
                {latestResults.length} results analyzed
              </span>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-20">
                <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
              </div>
            ) : latestResults.length === 0 ? (
              <div className="text-center py-20 text-gray-500">
                <TrendingUp className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>No results analyzed yet. Process some companies from the Calendar tab!</p>
              </div>
            ) : (
              <div className="space-y-6">
                {latestResults.map((result, idx) => (
                  <div 
                    key={idx}
                    className="p-6 bg-gray-800/50 border border-gray-700 rounded-xl hover:border-green-500/50 transition-all"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-2xl font-bold text-white">{result.company_name}</h3>
                        <p className="text-sm text-gray-500">{new Date(result.analyzed_at).toLocaleString()}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        (result.metrics.yoy_growth > 5) 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {(result.metrics.yoy_growth > 5) ? '📈 Beat' : '📉 Miss'}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="p-3 bg-gray-900/50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Revenue</p>
                        <p className="text-lg font-bold text-white">
                          ₹{result.metrics.revenue?.toLocaleString() || 'N/A'}Cr
                        </p>
                        {renderTrendIndicator(result.metrics.yoy_growth)}
                      </div>
                      <div className="p-3 bg-gray-900/50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Profit</p>
                        <p className="text-lg font-bold text-white">
                          ₹{result.metrics.profit_after_tax?.toLocaleString() || 'N/A'}Cr
                        </p>
                        {renderTrendIndicator(result.metrics.qoq_growth)}
                      </div>
                      <div className="p-3 bg-gray-900/50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">EPS</p>
                        <p className="text-lg font-bold text-white">₹{result.metrics.eps || 'N/A'}</p>
                      </div>
                    </div>

                    {result.insights && (
                      <div className="p-4 bg-gradient-to-r from-cyan-500/5 to-green-500/5 border border-cyan-500/20 rounded-lg">
                        <p className="text-sm text-gray-300 leading-relaxed">
                          <Brain className="inline w-4 h-4 text-cyan-400 mr-2" />
                          {result.insights}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div>
            <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
              <MessageSquare className="w-8 h-8 text-cyan-400" />
              Ask AI Anything
            </h2>
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden">
              <div className="h-96 overflow-y-auto p-6 space-y-4">
                {chatMessages.map((msg, idx) => (
                  <div 
                    key={idx}
                    className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-2xl p-4 rounded-lg ${
                      msg.type === 'user' 
                        ? 'bg-cyan-500 text-black' 
                        : 'bg-gray-700 text-white'
                    }`}>
                      {msg.text}
                    </div>
                  </div>
                ))}
              </div>
              <form onSubmit={handleChatSubmit} className="p-4 border-t border-gray-700 flex items-center gap-3">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask about any company's results..."
                  className="flex-1 px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:border-cyan-500 focus:outline-none"
                />
                <button 
                  type="submit"
                  disabled={!chatInput.trim()}
                  className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-black font-semibold rounded-lg transition-all"
                >
                  Send
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;