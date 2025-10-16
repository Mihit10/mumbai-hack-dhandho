import React from 'react';
import { Zap, Brain, Bell, Calendar, ArrowRight, BarChart3, Sparkles } from 'lucide-react';

const LandingPage = ({ onEnterDashboard }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-green-500/10"></div>
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-green-500/20 rounded-full blur-3xl animate-pulse delay-700"></div>
        </div>
        
        <nav className="relative z-10 flex justify-between items-center px-8 py-6">
          <div className="flex items-center gap-2">
            <Zap className="w-8 h-8 text-cyan-400" />
            <span className="text-2xl font-bold text-white">Khabri</span>
          </div>
          <button 
            onClick={onEnterDashboard}
            className="px-6 py-2 bg-cyan-500 hover:bg-cyan-600 text-black font-semibold rounded-lg transition-all duration-300 hover:scale-105"
          >
            Launch App
          </button>
        </nav>

        <div className="relative z-10 max-w-6xl mx-auto px-8 py-20 text-center">
          <div className="inline-block mb-4 px-4 py-2 bg-cyan-500/20 border border-cyan-500/50 rounded-full text-cyan-400 text-sm font-semibold">
            🚀 Your Unfair Advantage, Legally
          </div>
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Know Before<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-green-400">
              The Street Does
            </span>
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            AI-powered real-time stock results tracker. Get quarterly financials analyzed instantly — before the news breaks, before the price moves.
          </p>
          <button 
            onClick={onEnterDashboard}
            className="group px-8 py-4 bg-gradient-to-r from-cyan-500 to-green-500 hover:from-cyan-600 hover:to-green-600 text-black font-bold rounded-lg text-lg transition-all duration-300 hover:scale-105 flex items-center gap-2 mx-auto"
          >
            Start Tracking Results
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative z-10 max-w-6xl mx-auto px-8 py-20">
        <h2 className="text-4xl font-bold text-white text-center mb-12">
          Why Smart Money Uses Khabri
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: <Zap className="w-8 h-8" />,
              title: 'Lightning Fast',
              desc: 'Results analyzed in <60 seconds. Be first, always.',
              color: 'cyan'
            },
            {
              icon: <Brain className="w-8 h-8" />,
              title: 'AI-Powered Insights',
              desc: 'Multi-agent AI spots trends, red flags, and opportunities.',
              color: 'green'
            },
            {
              icon: <Bell className="w-8 h-8" />,
              title: 'Real-Time Alerts',
              desc: 'Push notifications the moment results drop.',
              color: 'cyan'
            }
          ].map((feature, idx) => (
            <div 
              key={idx}
              className="group p-6 bg-gray-800/50 border border-gray-700 rounded-xl hover:border-cyan-500/50 transition-all duration-300 hover:scale-105"
            >
              <div className={`inline-block p-3 bg-${feature.color}-500/20 rounded-lg mb-4 text-${feature.color}-400`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="relative z-10 max-w-6xl mx-auto px-8 py-20">
        <h2 className="text-4xl font-bold text-white text-center mb-12">
          Multi-Agent AI System
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { step: '1', title: 'Date Scraper', desc: 'Monitors NSE/BSE for result announcements', icon: Calendar },
            { step: '2', title: 'PDF Fetcher', desc: 'Grabs results from company websites instantly', icon: BarChart3 },
            { step: '3', title: 'AI Parser', desc: 'Extracts financials using LLM reasoning', icon: Brain },
            { step: '4', title: 'Analyzer', desc: 'Generates insights & detects red flags', icon: Sparkles }
          ].map((item, idx) => (
            <div key={idx} className="relative">
              <div className="p-6 bg-gradient-to-br from-gray-800/80 to-gray-900/80 border border-gray-700 rounded-xl">
                <div className="absolute -top-3 -left-3 w-8 h-8 bg-cyan-500 rounded-full flex items-center justify-center text-black font-bold text-sm">
                  {item.step}
                </div>
                <item.icon className="w-10 h-10 text-cyan-400 mb-4" />
                <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </div>
              {idx < 3 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 w-6 h-0.5 bg-cyan-500/50"></div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative z-10 max-w-4xl mx-auto px-8 py-20 text-center">
        <div className="p-12 bg-gradient-to-r from-cyan-500/10 to-green-500/10 border border-cyan-500/30 rounded-2xl">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Trade Smarter?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join traders who refuse to be late to the party.
          </p>
          <button 
            onClick={onEnterDashboard}
            className="px-8 py-4 bg-cyan-500 hover:bg-cyan-600 text-black font-bold rounded-lg text-lg transition-all duration-300 hover:scale-105"
          >
            Get Started Free
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;