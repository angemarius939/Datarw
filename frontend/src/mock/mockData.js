// Mock data for DataRW platform
export const mockOrganizations = [
  {
    id: "org_1",
    name: "Research Institute Rwanda",
    plan: "Professional",
    surveyCount: 7,
    storageUsed: 2.1,
    storageLimit: 3,
    users: 15,
    createdAt: "2024-01-15",
    status: "active"
  },
  {
    id: "org_2", 
    name: "Health Analytics Corp",
    plan: "Basic",
    surveyCount: 3,
    storageUsed: 0.8,
    storageLimit: 1,
    users: 5,
    createdAt: "2024-02-20",
    status: "active"
  }
];

export const mockSurveys = [
  {
    id: "survey_1",
    title: "Customer Satisfaction Survey",
    description: "Quarterly customer feedback collection",
    status: "active",
    responses: 245,
    createdAt: "2024-03-01",
    updatedAt: "2024-03-15",
    questions: [
      {
        id: "q1",
        type: "multiple_choice",
        question: "How satisfied are you with our service?",
        options: ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"],
        required: true
      },
      {
        id: "q2", 
        type: "text",
        question: "What can we improve?",
        required: false
      },
      {
        id: "q3",
        type: "rating",
        question: "Rate our support team",
        scale: 5,
        required: true
      }
    ]
  },
  {
    id: "survey_2",
    title: "Employee Engagement Survey",
    description: "Annual employee satisfaction assessment",
    status: "draft",
    responses: 0,
    createdAt: "2024-03-10",
    updatedAt: "2024-03-10",
    questions: []
  }
];

export const mockUsers = [
  {
    id: "user_1",
    name: "Jean Paul Mugisha",
    email: "jean@research.rw",
    role: "Admin",
    status: "active",
    lastLogin: "2024-03-15T10:30:00Z",
    surveysCreated: 5
  },
  {
    id: "user_2",
    name: "Marie Claire Uwimana",
    email: "marie@research.rw", 
    role: "Editor",
    status: "active",
    lastLogin: "2024-03-14T15:45:00Z",
    surveysCreated: 2
  },
  {
    id: "user_3",
    name: "Patrick Nkurunziza",
    email: "patrick@research.rw",
    role: "Viewer", 
    status: "active",
    lastLogin: "2024-03-13T09:15:00Z",
    surveysCreated: 0
  }
];

export const mockAnalytics = {
  totalResponses: 1250,
  responseRate: 68.5,
  averageCompletionTime: 4.2,
  topPerformingSurvey: "Customer Satisfaction Survey",
  monthlyGrowth: 15.3,
  storageGrowth: 12.8,
  responsesByMonth: [
    { month: "Jan", responses: 180 },
    { month: "Feb", responses: 220 },
    { month: "Mar", responses: 285 },
    { month: "Apr", responses: 310 },
    { month: "May", responses: 255 }
  ],
  surveyTypes: [
    { type: "Customer Feedback", count: 45, percentage: 35 },
    { type: "Employee Surveys", count: 32, percentage: 25 },
    { type: "Market Research", count: 28, percentage: 22 },
    { type: "Product Feedback", count: 23, percentage: 18 }
  ]
};

export const pricingPlans = [
  {
    name: "Basic",
    price: "100,000",
    currency: "FRW",
    period: "month",
    surveys: 4,
    storage: "1 GB",
    users: "5 users",
    features: [
      "4 active surveys", 
      "1 GB data storage",
      "Basic analytics",
      "Email support",
      "Data export (CSV)"
    ],
    popular: false
  },
  {
    name: "Professional", 
    price: "300,000",
    currency: "FRW",
    period: "month",
    surveys: 10,
    storage: "3 GB", 
    users: "20 users",
    features: [
      "10 active surveys",
      "3 GB data storage", 
      "Advanced analytics",
      "Priority support",
      "Multiple export formats",
      "Skip logic & calculations",
      "Custom branding"
    ],
    popular: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    currency: "",
    period: "",
    surveys: "Unlimited",
    storage: "Unlimited",
    users: "Unlimited users",
    features: [
      "Unlimited surveys",
      "Unlimited storage",
      "Advanced KPI dashboards", 
      "24/7 dedicated support",
      "API access",
      "White-label solution",
      "Custom integrations",
      "Advanced user management"
    ],
    popular: false
  }
];

export const questionTypes = [
  {
    type: "multiple_choice",
    name: "Multiple Choice",
    icon: "☑️",
    description: "Single or multiple selection from options"
  },
  {
    type: "text",
    name: "Text Input", 
    icon: "📝",
    description: "Short or long text responses"
  },
  {
    type: "rating",
    name: "Rating Scale",
    icon: "⭐",
    description: "1-5 or 1-10 rating scale"
  },
  {
    type: "file_upload",
    name: "File Upload",
    icon: "📎", 
    description: "Allow respondents to upload files"
  },
  {
    type: "calculation",
    name: "Calculation",
    icon: "🔢",
    description: "Calculate values from other fields"
  },
  {
    type: "skip_logic",
    name: "Skip Logic",
    icon: "↩️",
    description: "Conditional question flow"
  }
];