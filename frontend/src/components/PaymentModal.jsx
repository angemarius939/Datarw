import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { 
  CreditCard, 
  Smartphone, 
  Building2, 
  Check, 
  X, 
  Clock, 
  AlertCircle,
  Loader2,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { paymentsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const PaymentModal = ({ 
  isOpen, 
  onClose, 
  selectedPlan = null, 
  onPaymentSuccess,
  onPaymentError 
}) => {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [paymentData, setPaymentData] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('idle');
  
  // Form data
  const [formData, setFormData] = useState({
    user_name: user?.name || '',
    user_email: user?.email || '',
    phone_number: '',
    payment_method: 'MTN',
    selected_plan: selectedPlan || 'Basic'
  });
  
  // Available plans
  const [pricingPlans, setPricingPlans] = useState({
    Basic: { price: 100000, currency: 'RWF', features: ['10 Surveys', '100 Responses', 'Basic Analytics'] },
    Professional: { price: 300000, currency: 'RWF', features: ['Unlimited Surveys', '10K Responses', 'Advanced Analytics', 'API Access'] },
    Enterprise: { price: 'Custom', currency: 'RWF', features: ['Unlimited Everything', 'Priority Support', 'Custom Integrations'] }
  });

  useEffect(() => {
    if (isOpen) {
      fetchPricingPlans();
      setCurrentStep(1);
      setPaymentStatus('idle');
      setError('');
      setPaymentData(null);
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedPlan) {
      setFormData(prev => ({ ...prev, selected_plan: selectedPlan }));
    }
  }, [selectedPlan]);

  const fetchPricingPlans = async () => {
    try {
      const response = await paymentsAPI.getPricingPlans();
      if (response.data.success) {
        setPricingPlans(response.data.plans);
      }
    } catch (error) {
      console.error('Error fetching pricing plans:', error);
    }
  };

  const validatePhoneNumber = (phone) => {
    const phoneRegex = /^07[0-9]{8}$/;
    return phoneRegex.test(phone);
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    
    if (!validatePhoneNumber(formData.phone_number)) {
      setError('Please enter a valid Rwandan phone number (07XXXXXXXX)');
      return;
    }

    if (formData.selected_plan === 'Enterprise') {
      setError('Enterprise plan requires custom pricing. Please contact our sales team.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Create subscription payment
      const response = await paymentsAPI.createSubscriptionPayment({
        user_name: formData.user_name,
        user_email: formData.user_email,
        phone_number: formData.phone_number,
        plan_name: formData.selected_plan,
        payment_method: formData.payment_method
      });

      if (response.data.success) {
        setPaymentData(response.data.data);
        setCurrentStep(2);
        setPaymentStatus('processing');
        
        // Start monitoring payment status
        monitorPaymentStatus(response.data.data.invoice.invoiceNumber);
      }
    } catch (error) {
      console.error('Error creating payment:', error);
      setError(error.response?.data?.detail || 'Failed to create payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const monitorPaymentStatus = async (invoiceNumber) => {
    const checkStatus = async () => {
      try {
        const statusResponse = await paymentsAPI.getPaymentStatus(invoiceNumber);
        const status = statusResponse.data.status;
        
        setPaymentStatus(status);
        
        if (status === 'completed') {
          setCurrentStep(3);
          if (onPaymentSuccess) {
            onPaymentSuccess(statusResponse.data);
          }
        } else if (status === 'failed') {
          setCurrentStep(4);
          setError('Payment failed. Please try again or contact support.');
          if (onPaymentError) {
            onPaymentError(new Error('Payment failed'));
          }
        } else if (status === 'expired') {
          setCurrentStep(4);
          setError('Payment session expired. Please start a new payment.');
          if (onPaymentError) {
            onPaymentError(new Error('Payment expired'));
          }
        } else if (status === 'processing' || status === 'pending') {
          // Continue monitoring
          setTimeout(checkStatus, 3000);
        }
      } catch (error) {
        console.error('Error checking payment status:', error);
        setTimeout(checkStatus, 5000); // Retry after 5 seconds
      }
    };
    
    // Start checking after 3 seconds
    setTimeout(checkStatus, 3000);
  };

  const handleClose = () => {
    setCurrentStep(1);
    setPaymentStatus('idle');
    setError('');
    setPaymentData(null);
    onClose();
  };

  const getPaymentMethodIcon = (method) => {
    switch (method) {
      case 'MTN':
        return <Smartphone className="h-5 w-5 text-yellow-600" />;
      case 'AIRTEL':
        return <Smartphone className="h-5 w-5 text-red-600" />;
      case 'CARD':
        return <CreditCard className="h-5 w-5 text-blue-600" />;
      case 'BANK':
        return <Building2 className="h-5 w-5 text-green-600" />;
      default:
        return <Smartphone className="h-5 w-5" />;
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-between mb-6">
      {[1, 2, 3].map((step) => (
        <div key={step} className="flex items-center">
          <div className={`
            flex items-center justify-center w-8 h-8 rounded-full
            ${currentStep >= step 
              ? (currentStep === step ? 'bg-blue-600 text-white' : 'bg-green-600 text-white')
              : 'bg-gray-200 text-gray-600'
            }
          `}>
            {currentStep > step ? <Check className="h-4 w-4" /> : step}
          </div>
          {step < 3 && (
            <div className={`
              w-16 h-0.5 mx-2
              ${currentStep > step ? 'bg-green-600' : 'bg-gray-200'}
            `} />
          )}
        </div>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <form onSubmit={handleFormSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {Object.entries(pricingPlans).map(([planName, plan]) => (
          <Card 
            key={planName}
            className={`cursor-pointer transition-all ${
              formData.selected_plan === planName 
                ? 'ring-2 ring-blue-500 shadow-lg' 
                : 'hover:shadow-md'
            }`}
            onClick={() => setFormData(prev => ({ ...prev, selected_plan: planName }))}
          >
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-lg">{planName}</CardTitle>
              <div className="text-3xl font-bold text-blue-600">
                {plan.price === 'Custom' ? 'Custom' : `${plan.price.toLocaleString()} ${plan.currency}`}
              </div>
              {plan.price !== 'Custom' && (
                <CardDescription>per month</CardDescription>
              )}
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-sm">
                    <Check className="h-4 w-4 text-green-500 mr-2" />
                    {feature}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="user_name">Full Name</Label>
          <Input
            id="user_name"
            value={formData.user_name}
            onChange={(e) => setFormData(prev => ({ ...prev, user_name: e.target.value }))}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="user_email">Email Address</Label>
          <Input
            id="user_email"
            type="email"
            value={formData.user_email}
            onChange={(e) => setFormData(prev => ({ ...prev, user_email: e.target.value }))}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="phone_number">Phone Number</Label>
          <Input
            id="phone_number"
            placeholder="07XXXXXXXX"
            value={formData.phone_number}
            onChange={(e) => setFormData(prev => ({ ...prev, phone_number: e.target.value }))}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="payment_method">Payment Method</Label>
          <Select value={formData.payment_method} onValueChange={(value) => setFormData(prev => ({ ...prev, payment_method: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="MTN">
                <div className="flex items-center">
                  <Smartphone className="h-4 w-4 text-yellow-600 mr-2" />
                  MTN Mobile Money
                </div>
              </SelectItem>
              <SelectItem value="AIRTEL">
                <div className="flex items-center">
                  <Smartphone className="h-4 w-4 text-red-600 mr-2" />
                  Airtel Money
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex justify-between">
        <Button type="button" variant="outline" onClick={handleClose}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? (
            <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Processing...</>
          ) : (
            <>Pay {pricingPlans[formData.selected_plan]?.price !== 'Custom' ? `${pricingPlans[formData.selected_plan]?.price.toLocaleString()} RWF` : 'Custom Amount'}</>
          )}
        </Button>
      </div>
    </form>
  );

  const renderStep2 = () => (
    <div className="text-center space-y-6">
      <div className="flex justify-center">
        <div className="relative">
          <Loader2 className="h-16 w-16 text-blue-600 animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            {getPaymentMethodIcon(formData.payment_method)}
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-xl font-semibold mb-2">Payment Initiated</h3>
        <p className="text-gray-600 mb-4">
          {formData.payment_method === 'MTN' 
            ? `A payment request has been sent to your MTN Mobile Money account (${formData.phone_number}). Please check your phone and confirm the payment.`
            : `A payment request has been sent to your Airtel Money account (${formData.phone_number}). Please check your phone and confirm the payment.`
          }
        </p>
        
        {paymentData && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Amount:</span> {paymentData.amount.toLocaleString()} RWF
              </div>
              <div>
                <span className="font-medium">Plan:</span> {formData.selected_plan}
              </div>
              <div>
                <span className="font-medium">Payment Method:</span> {formData.payment_method}
              </div>
              <div>
                <span className="font-medium">Reference:</span> {paymentData.payment?.paymentReference}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
        <Clock className="h-4 w-4" />
        <span>Estimated processing time: 2-5 minutes</span>
      </div>

      <Progress value={50} className="w-full" />
      
      <div className="text-sm text-gray-500">
        Waiting for payment confirmation...
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="text-center space-y-6">
      <div className="flex justify-center">
        <div className="bg-green-100 p-4 rounded-full">
          <CheckCircle className="h-16 w-16 text-green-600" />
        </div>
      </div>

      <div>
        <h3 className="text-2xl font-bold text-green-600 mb-2">Payment Successful!</h3>
        <p className="text-gray-600 mb-4">
          Your subscription to the {formData.selected_plan} plan has been activated successfully.
        </p>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="font-semibold text-green-800 mb-2">What's Next?</h4>
          <ul className="text-sm text-green-700 text-left space-y-1">
            <li>• Your account has been upgraded to {formData.selected_plan} plan</li>
            <li>• You now have access to all {formData.selected_plan} features</li>
            <li>• Your subscription is valid for 30 days</li>
            <li>• You'll receive a confirmation email shortly</li>
          </ul>
        </div>
      </div>

      <Button onClick={handleClose} className="w-full">
        Continue to Dashboard
      </Button>
    </div>
  );

  const renderStep4 = () => (
    <div className="text-center space-y-6">
      <div className="flex justify-center">
        <div className="bg-red-100 p-4 rounded-full">
          <XCircle className="h-16 w-16 text-red-600" />
        </div>
      </div>

      <div>
        <h3 className="text-2xl font-bold text-red-600 mb-2">Payment Failed</h3>
        <p className="text-gray-600 mb-4">
          Unfortunately, your payment could not be processed.
        </p>
        
        <div className="bg-red-50 p-4 rounded-lg">
          <h4 className="font-semibold text-red-800 mb-2">Common Issues:</h4>
          <ul className="text-sm text-red-700 text-left space-y-1">
            <li>• Insufficient funds in your mobile money account</li>
            <li>• Payment was cancelled on your mobile device</li>
            <li>• Network connectivity issues</li>
            <li>• Payment session expired</li>
          </ul>
        </div>
      </div>

      <div className="flex gap-3">
        <Button variant="outline" onClick={handleClose} className="flex-1">
          Close
        </Button>
        <Button 
          onClick={() => {
            setCurrentStep(1);
            setPaymentStatus('idle');
            setError('');
            setPaymentData(null);
          }} 
          className="flex-1"
        >
          Try Again
        </Button>
      </div>
    </div>
  );

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">Subscribe to DataRW</DialogTitle>
          <DialogDescription>
            Choose your plan and complete the payment to upgrade your account
          </DialogDescription>
        </DialogHeader>

        <div className="mt-6">
          {currentStep < 4 && renderStepIndicator()}
          
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
          {currentStep === 4 && renderStep4()}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PaymentModal;