import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import Dashboard from "./components/Dashboard";
import AuthModal from "./components/AuthModal";
import PaymentModal from "./components/PaymentModal";
import { Toaster } from "./components/ui/toaster";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  // Check for payment results on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const paymentSuccess = urlParams.get('payment_success');
    const paymentCancelled = urlParams.get('payment_cancelled');
    
    if (paymentSuccess) {
      // Handle successful payment
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    if (paymentCancelled) {
      // Handle cancelled payment
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleGetStarted = (plan = null) => {
    if (isAuthenticated) {
      if (plan) {
        setSelectedPlan(plan);
        setShowPaymentModal(true);
      }
    } else {
      setShowAuthModal(true);
    }
  };

  const handleUpgrade = (plan) => {
    setSelectedPlan(plan);
    setShowPaymentModal(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mb-4 mx-auto">
            <span className="text-white font-bold text-xl">D</span>
          </div>
          <p className="text-gray-600">Loading DataRW...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            isAuthenticated ? (
              <Dashboard onUpgrade={handleUpgrade} />
            ) : (
              <LandingPage onGetStarted={handleGetStarted} />
            )
          } />
        </Routes>
      </BrowserRouter>
      
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
      />
      
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        selectedPlan={selectedPlan}
      />
      
      <Toaster />
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
