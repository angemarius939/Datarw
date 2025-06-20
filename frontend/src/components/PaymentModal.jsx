import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { CheckCircle, Loader2, CreditCard, Star } from 'lucide-react';
import { paymentAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const PaymentModal = ({ isOpen, onClose, selectedPlan = null }) => {
  const { organization, updateOrganization } = useAuth();
  const [plans, setPlans] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchPlans();
    }
  }, [isOpen]);

  const fetchPlans = async () => {
    try {
      const response = await paymentAPI.getPaymentPlans();
      setPlans(response.data);
    } catch (error) {
      console.error('Error fetching plans:', error);
      setError('Failed to load payment plans');
    }
  };

  const handleUpgrade = async (planName) => {
    if (planName === 'Enterprise') {
      window.open('mailto:sales@datarw.com?subject=Enterprise Plan Inquiry', '_blank');
      return;
    }

    setProcessing(true);
    setError('');

    try {
      const response = await paymentAPI.createCheckoutSession(planName);
      const { url } = response.data;
      
      // Redirect to Stripe checkout
      window.location.href = url;
    } catch (error) {
      console.error('Payment error:', error);
      setError(error.response?.data?.detail || 'Failed to create payment session');
      setProcessing(false);
    }
  };

  const formatPrice = (amount, currency) => {
    if (!amount) return 'Custom';
    return new Intl.NumberFormat('en-RW', {
      style: 'currency',
      currency: currency === 'FRW' ? 'RWF' : currency,
      minimumFractionDigits: 0
    }).format(amount);
  };

  const PlanCard = ({ planName, planData }) => {
    const isCurrentPlan = organization?.plan === planName;
    const isPopular = planName === 'Professional';
    
    return (
      <Card className={`relative ${isPopular ? 'border-blue-500 shadow-lg' : ''} ${isCurrentPlan ? 'bg-green-50 border-green-500' : ''}`}>
        {isPopular && (
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
            <Badge className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1">
              <Star className="w-3 h-3 mr-1" /> Most Popular
            </Badge>
          </div>
        )}
        
        {isCurrentPlan && (
          <div className="absolute -top-4 right-4">
            <Badge className="bg-green-600 text-white px-3 py-1">
              <CheckCircle className="w-3 h-3 mr-1" /> Current Plan
            </Badge>
          </div>
        )}

        <CardHeader className="text-center pb-4">
          <CardTitle className="text-2xl font-bold">{planName}</CardTitle>
          <div className="mt-4">
            <span className="text-4xl font-bold">
              {formatPrice(planData.amount, planData.currency)}
            </span>
            {planData.amount && (
              <span className="text-gray-600 ml-2">/month</span>
            )}
          </div>
          <CardDescription className="mt-2">
            {planData.survey_limit === -1 ? 'Unlimited' : planData.survey_limit} surveys • 
            {planData.storage_limit === -1 ? ' Unlimited' : ` ${planData.storage_limit}GB`} storage
          </CardDescription>
        </CardHeader>

        <CardContent>
          <ul className="space-y-3 mb-6">
            {planData.features?.map((feature, index) => (
              <li key={index} className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">{feature}</span>
              </li>
            ))}
          </ul>

          <Button
            onClick={() => handleUpgrade(planName)}
            disabled={processing || isCurrentPlan}
            className={`w-full ${
              isCurrentPlan 
                ? 'bg-green-600 hover:bg-green-700' 
                : isPopular 
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700' 
                  : 'bg-gray-900 hover:bg-gray-800'
            }`}
          >
            {processing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isCurrentPlan ? (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                Current Plan
              </>
            ) : planName === 'Enterprise' ? (
              'Contact Sales'
            ) : (
              <>
                <CreditCard className="mr-2 h-4 w-4" />
                Upgrade to {planName}
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-center">
            Choose Your Plan
          </DialogTitle>
          <DialogDescription className="text-center">
            Upgrade your account to unlock more features and increase your limits
          </DialogDescription>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid md:grid-cols-3 gap-6 mt-6">
          {Object.entries(plans).map(([planName, planData]) => (
            <PlanCard key={planName} planName={planName} planData={planData} />
          ))}
        </div>

        <div className="text-center text-sm text-gray-600 mt-6">
          <p>All plans include SSL security, regular backups, and email support.</p>
          <p>You can cancel or change your plan at any time.</p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PaymentModal;