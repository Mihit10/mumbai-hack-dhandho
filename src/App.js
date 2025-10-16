import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';

function App() {
  const [showDashboard, setShowDashboard] = useState(false);

  return showDashboard 
    ? <Dashboard onBackToHome={() => setShowDashboard(false)} /> 
    : <LandingPage onEnterDashboard={() => setShowDashboard(true)} />;
}

export default App;