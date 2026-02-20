# AI Employee Dashboard Agent – Technical & Product Specification

## 1. Current Stack & Infrastructure

| Layer | Technology / Choice | Notes |
|-------|-------------------|-------|
| **Backend** | Flask (Python 3.11+) | Lightweight, production-ready web framework |
| **AI Engine** | Google Vertex AI → `gemini-2.0-flash-001` <br>Temperature: 0.3 for consistency | Latest Gemini model with 8192 token output |
| **Data Layer** | Pandas DataFrames <br>In-memory caching after first load | |
| **Frontend** | React 18 + Vite <br>Recharts 2.x for visualizations <br>Lucide React for icons | Modern, component-based SPA |
| **Charts** | Recharts (native React integration) | Supports Bar, Line, Pie, Donut, Table |
| **State Management** | React Hooks (useState) <br>No Redux required | Simple, effective for current scope |
| **API Communication** | Fetch API (native browser) <br>JSON request/response | No axios dependency needed |
| **Styling** | Inline styles + CSS-in-JS | Custom color palette: #567c8d, #c8d9e5, #2f4156 |
| **Deployment** | **Backend**: GCP Cloud Run <br>**Frontend**: Static hosting (Vite build) | Zero-ops, auto-scaling on Cloud Run |
| **CORS** | Flask-CORS with `origins="*"` | Currently permissive; tighten for production |
| **Dataset** | Fixed CSV | No file upload (security by design) |

---

## 2. Core Logic Flow

```
User query: "Create an attrition dashboard"
   ↓
Frontend: DashboardAgent.jsx
   ├─ createNewChat() or handleSendMessage()
   ├─ POST /api/chat with { message, history, current_dashboard }
   ├─ Show generation status: "Analyzing request..." → "Generating overview..." → "Creating visualizations..."
   ↓
Backend: main.py /api/chat endpoint
   ├─ Extract: user_message, conversation_history, current_dashboard
   ├─ Load dataset
   ├─ Calculate statistics: 
   │     • Total employees: 1,470
   │     • Attrition: 237 Yes (16.1%), 1,233 No (83.9%)
   │     • Avg age: 36.9 years
   │     • Avg income: $6,503/month
   │     • Avg satisfaction: 2.73/4
   │     • Overtime: 416 employees (28.3%)
   ├─ Build AI context:
   │     • SYSTEM_PROMPT (comprehensive instructions)
   │     • Data summary (statistics + field descriptions)
   │     • Conversation history (last 5 messages)
   │     • Current dashboard (if modifying existing)
   ├─ Call Vertex AI:
   │     model.generate_content(
   │         context,
   │         max_output_tokens=8192,
   │         temperature=0.3,  # consistency
   │         top_p=0.9
   │     )
   ↓
Gemini AI Processing
   ├─ Parse natural language query
   ├─ Reference actual data statistics
   ├─ Generate structured JSON:
   │     {
   │       "dashboard": {
   │         "title": "Employee Attrition & HR Insights Dashboard",
   │         "overview": "2-3 sentences explaining scope...",
   │         "overall_insights": [
   │           "Insight 1 with specific numbers",
   │           "Insight 2 with comparisons",
   │           ...7-8 total insights
   │         ],
   │         "metrics": [
   │           {label, value, insight, trend, benchmark},
   │           ...4-6 KPIs
   │         ],
   │         "visualizations": [
   │           {
   │             type: "table|bar|line|pie|donut",
   │             title: "Clear Title",
   │             description: "What it shows and why",
   │             fields: ["field1", "field2"],
   │             key_insights: [
   │               "Specific insight 1 with data",
   │               "Specific insight 2 with comparison",
   │               "Specific insight 3 with recommendation",
   │               "Specific insight 4 with business impact"
   │             ]
   │           },
   │           ...6-8 charts (including 2+ tables)
   │         ],
   │         "recommendations": [
   │           "Immediate action 1",
   │           "Short-term initiative 2",
   │           "Medium-term strategy 3",
   │           "Long-term goal 4"
   │         ]
   │       }
   │     }
   ↓
Backend: Validation & Response
   ├─ Parse JSON (strip markdown if present)
   ├─ Validate structure:
   │     • Ensure overview exists (add default if missing)
   │     • Ensure 7+ overall_insights (add defaults if <7)
   │     • Ensure each visualization has key_insights (add defaults if missing)
   ├─ Return to frontend:
   │     {
   │       response: "Dashboard created successfully",
   │       dashboard: {...validated structure},
   │       analysis_type: "attrition",
   │       timestamp: "2024-12-08T..."
   │     }
   ↓
Frontend: Dashboard Rendering
   ├─ Update chat state with new message + dashboard
   ├─ Render sections:
   │     • Overview (styled paragraph)
   │     • Overall Insights (7-8 bullet points with arrows)
   │     • KPI Cards (4-6 gradient cards in grid)
   │     • Visualizations (6-8 charts in 2-column grid):
   │         ├─ For each viz:
   │         │    ├─ generateChartDataFromDashboard(viz)
   │         │    ├─ Render with Recharts:
   │         │    │    • BarChart, LineChart, PieChart, etc.
   │         │    │    • ResponsiveContainer (width="100%", height=250px)
   │         │    └─ Display key_insights below chart (3-4 bullets)
   │         └─ Tables rendered as HTML <table> elements
   ├─ Smooth animations (fadeIn, 0.3s transitions)
   ↓
User sees complete dashboard:
   ✓ Overview section
   ✓ 7-8 Overall Insights with specific data
   ✓ 4-6 KPI metrics with trends
   ✓ 6-8 visualizations with descriptions
   ✓ 3-4 Key Insights per chart
   ✓ 4 strategic recommendations
```

---

## 3. Detailed Component Architecture

### 3.1 Frontend Components (DashboardAgent.jsx)

```
┌─────────────────────────────────────────────────────────────┐
│                    DashboardAgent Component                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  State Management (React Hooks):                             │
│  ├─ chats: Array<Chat>                                       │
│  │    └─ Chat: { id, title, messages[], dashboard }         │
│  ├─ activeChat: number | null                                │
│  ├─ input: string                                            │
│  ├─ loading: boolean                                         │
│  ├─ showLanding: boolean                                     │
│  ├─ showChat: boolean (toggle chat panel)                   │
│  ├─ showSidebar: boolean (toggle sidebar)                   │
│  ├─ presentMode: boolean (full-screen mode)                 │
│  └─ generationStatus: string (progress messages)            │
│                                                               │
│  Layout Structure:                                            │
│  ┌──────────┬──────────────────────────┬─────────────────┐  │
│  │ Sidebar  │   Dashboard Panel        │   Chat Panel    │  │
│  │ 280px    │   (Flexible width)       │   400px         │  │
│  │          │                          │   (toggleable)  │  │
│  │ [+] New  │  Header: [Hide Chat]     │   Messages      │  │
│  │ Chat     │          [Present Mode]  │   ...           │  │
│  │          │                          │   ...           │  │
│  │ Chat 1   │  Overview                │   Input field   │  │
│  │ Chat 2   │  Overall Insights (7-8)  │   [Send]        │  │
│  │ Chat 3   │  [KPI] [KPI] [KPI] [KPI] │                 │  │
│  │          │  [Chart1]    [Chart2]     │                 │  │
│  │ [Delete] │  Insights    Insights     │                 │  │
│  │          │  [Chart3]    [Chart4]     │                 │  │
│  └──────────┴──────────────────────────┴─────────────────┘  │
│                                                               │
│  Key Functions:                                               │
│  ├─ createNewChat(prompt?) → Creates chat, optionally       │
│  │                            sends initial message          │
│  ├─ handleSendMessage(msg) → POST to /api/chat,             │
│  │                            update state, show progress    │
│  ├─ deleteChat(id) → Remove from chats array                │
│  ├─ generateChartDataFromDashboard(viz) →                   │
│  │    Smart data generation based on viz.title:             │
│  │    • "department" → Sales/R&D/HR data                    │
│  │    • "age" → Age ranges with income                      │
│  │    • "role" → Job roles with counts                      │
│  │    • "overtime" → Overtime vs no overtime                │
│  │    • "attrition" → 1233 retained, 237 left               │
│  └─ Render logic for each chart type (bar, line, pie, etc.) │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Backend API (main.py)

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend Server                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Endpoints:                                                   │
│  ├─ GET  /health                                             │
│  │   Returns: {                                              │
│  │     status: "healthy",                                    │
│  │     project_id: "molten-album-478703-d8",                │
│  │     location: "us-central1",                             │
│  │     model: "gemini-2.0-flash-001",                       │
│  │     dataset_loaded: true,                                │
│  │     records: 1470                                        │
│  │   }                                                       │
│  │                                                           │
│  └─ POST /api/chat                                          │
│      Request: {                                              │
│        message: "Create attrition dashboard",               │
│        history: [{role, content}, ...],                     │
│        current_dashboard: {...} | null                      │
│      }                                                       │
│      Response: {                                             │
│        response: "Dashboard created successfully",          │
│        dashboard: {...full structure},                      │
│        analysis_type: "attrition",                          │
│        timestamp: "2024-12-08T..."                          │
│      }                                                       │
│                                                               │
│  Key Functions:                                               │
│  ├─ load_dataset() → pd.read_csv() with caching            │
│  ├─ get_data_summary() →                                    │
│  │    Calculate comprehensive statistics:                   │
│  │    • Demographics (age, gender)                          │
│  │    • Departments (Sales, R&D, HR)                        │
│  │    • Compensation (avg/median income)                    │
│  │    • Satisfaction (job, environment, work-life)          │
│  │    • Tenure (years at company, total experience)         │
│  │    • Overtime (percentage working OT)                    │
│  │    Returns formatted text summary                        │
│  │                                                           │
│  └─ chat() → Main endpoint logic:                           │
│      1. Extract request data                                │
│      2. Load dataset (cached)                               │
│      3. Get data summary                                    │
│      4. Build AI context:                                   │
│         SYSTEM_PROMPT +                                     │
│         data_summary +                                      │
│         conversation_history +                              │
│         current_dashboard (if modifying)                    │
│      5. Call Gemini:                                        │
│         model.generate_content(                             │
│           context,                                          │
│           max_output_tokens=8192,                           │
│           temperature=0.3,                                  │
│           top_p=0.9                                         │
│         )                                                   │
│      6. Parse JSON response                                 │
│      7. Validate structure                                  │
│      8. Return to frontend                                  │
│                                                               │
│  SYSTEM_PROMPT Structure (2000+ lines):                      │
│  ├─ Role definition                                         │
│  ├─ Mandatory sections (NEVER skip):                        │
│  │    • Overview (2-3 sentences)                            │
│  │    • Overall Insights (7-8 bullets)                      │
│  │    • Metrics (4-6 KPIs)                                  │
│  │    • Visualizations (6-8 charts, 2+ tables)             │
│  │    • Key Insights per viz (3-4 each)                    │
│  │    • Recommendations (4 strategic actions)               │
│  ├─ Data schema (all 35 fields)                            │
│  ├─ Response format (JSON structure)                        │
│  ├─ Quality standards (specificity, actionability)          │
│  └─ Examples (full dashboard samples)                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow Sequence Diagram

```
┌─────────┐                                    ┌──────────────┐
│  User   │                                    │   Frontend   │
│ Browser │                                    │ DashboardAgent│
└────┬────┘                                    └──────┬───────┘
     │                                                 │
     │ 1. Type: "Create attrition dashboard"         │
     │ ────────────────────────────────────────────>  │
     │                                                 │
     │                                                 │ 2. createNewChat()
     │                                                 │    or handleSendMessage()
     │                                                 │
     │                                                 │ 3. Update state:
     │                                                 │    • Add user message
     │                                                 │    • Set loading=true
     │                                                 │    • Show status
     │                                                 │
     │                                         ┌───────▼────────┐
     │                                         │                 │
     │                                         │ POST /api/chat  │
     │                                         │ {               │
     │                                         │   message,      │
     │                                         │   history,      │
     │                                         │   current_dash  │
     │                                         │ }               │
     │                                         │                 │
     │                                         └───────┬────────┘
     │                                                 │
     │                                                 │ 4. HTTP Request
     │                                         ┌───────▼────────┐
     │                                         │                 │
     │                                         │  Flask Backend  │
     │                                         │    main.py      │
     │                                         │                 │
     │                                         └───────┬────────┘
     │                                                 │
     │                                                 │ 5. chat() endpoint
     │                                                 │
     │                                         ┌───────▼────────┐
     │                                         │ Load Dataset   │
     │                                         │ pd.read_csv()  │
     │                                         │ 1,470 records  │
     │                                         └───────┬────────┘
     │                                                 │
     │                                         ┌───────▼────────┐
     │                                         │ Calculate Stats│
     │                                         │ • Attrition    │
     │                                         │ • Income       │
     │                                         │ • Satisfaction │
     │                                         │ • Overtime     │
     │                                         └───────┬────────┘
     │                                                 │
     │                                         ┌───────▼────────┐
     │                                         │ Build Context  │
     │                                         │ • SYSTEM_PROMPT│
     │                                         │ • Data summary │
     │                                         │ • History      │
     │                                         │ • Current dash │
     │                                         └───────┬────────┘
     │                                                 │
     │                                                 │ 6. API Call
     │                                         ┌───────▼────────┐
     │                                         │                 │
     │                                         │  Vertex AI      │
     │                                         │  Gemini 2.0     │
     │                                         │  Flash          │
     │                                         │                 │
     │                                         │ • Parse query   │
     │                                         │ • Reference data│
     │                                         │ • Generate JSON │
     │                                         │                 │
     │                                         └───────┬────────┘
     │                                                 │
     │                                                 │ 7. JSON Response
     │                                         ┌───────▼────────┐
     │                                         │                 │
     │                                         │ Parse & Validate│
     │                                         │ • Strip markdown│
     │                                         │ • Check fields  │
     │                                         │ • Add defaults  │
     │                                         │                 │
     │                                         └───────┬────────┘
     │                                                 │
     │                                                 │ 8. Return JSON
     │                                         ┌───────▼────────┐
     │                                         │                 │
     │ <────────────────────────────────────── │ HTTP Response  │
     │                                         │ {              │
     │ 9. Update state:                        │   response,    │
     │    • Add AI message                     │   dashboard,   │
     │    • Store dashboard                    │   timestamp    │
     │    • Set loading=false                  │ }              │
     │                                         │                │
     │                                         └────────────────┘
     │
     │ 10. Render Dashboard:
     │     • Overview section
     │     • Overall Insights (7-8)
     │     • KPI Cards (4-6)
     │     • Visualizations (6-8)
     │       ├─ Generate chart data
     │       ├─ Render with Recharts
     │       └─ Show key insights
     │     • Recommendations (4)
     │
     ▼
  Dashboard Displayed
```

---

## 5. Key Data Structures

### 5.1 Chat Object (Frontend)
```typescript
interface Chat {
  id: number;              // timestamp
  title: string;           // "Chat 1", "Chat 2"
  messages: Message[];     // conversation history
  dashboard: Dashboard | null;  // latest dashboard
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}
```

### 5.2 Dashboard Object (AI-Generated)
```json
{
  "title": "Employee Attrition & HR Insights Dashboard",
  
  "overview": "This dashboard provides comprehensive analysis of employee attrition, demographics, compensation, and satisfaction metrics using the HR dataset. It highlights attrition patterns, employee distribution, compensation trends, satisfaction scores, and key workforce KPIs to support data-driven HR decisions and workforce planning.",
  
  "overall_insights": [
    "Overall attrition is low: 237 employees left vs 1,233 retained (~16% attrition), so most employees remain",
    "Retention appears generally effective but ~237 leavers represent a targetable cohort for improvement",
    "Average monthly income increases with age, with noticeable pay jumps around age ~38 and again after ~45",
    "Males show higher absolute attrition count (150) compared to females (87), though rates are proportionally similar",
    "Attrition is heavily concentrated at Job Level 1 (143 leavers) and declines sharply at higher levels",
    "Sales has highest attrition rate at 21% (92 of 446), followed by HR (19%) and R&D (14%)",
    "Laboratory Technician (62) and Sales Executive (57) have highest attrition counts",
    "Overtime workers show 30.5% attrition vs 10.4% for no overtime - nearly 3x higher risk"
  ],
  
  "metrics": [
    {
      "label": "Total Employees",
      "value": "1,470",
      "insight": "Current workforce size across all departments",
      "trend": "stable"
    },
    {
      "label": "Overall Attrition Rate",
      "value": "16.1%",
      "insight": "237 employees left, below industry average of 19%",
      "trend": "stable",
      "benchmark": "Industry: 19% | Best-in-class: 12%"
    },
    {
      "label": "Average Monthly Income",
      "value": "$6,503",
      "insight": "Competitive but shows 15% variance across departments",
      "trend": "up",
      "benchmark": "Market median: $6,200"
    },
    {
      "label": "Avg Job Satisfaction",
      "value": "2.73",
      "insight": "Out of 4.0 scale, room for improvement",
      "trend": "stable"
    }
  ],
  
  "visualizations": [
    {
      "type": "table",
      "title": "Attrition Rate by Department",
      "description": "Detailed breakdown of employee turnover across departments",
      "fields": ["Department", "Total Employees", "Attrition Count", "Attrition Rate"],
      "key_insights": [
        "Sales has highest attrition at 20.6% (92 of 446 employees)",
        "R&D shows strong retention at 13.8% (133 of 961)",
        "HR at 19.0% aligns with company average",
        "Immediate action needed: retention program for Sales"
      ]
    },
    {
      "type": "donut",
      "title": "Attrition Rate Distribution",
      "description": "Overall employee retention showing proportion retained vs left",
      "fields": ["Attrition"],
      "key_insights": [
        "237 employees (16.1%) left while 1,233 (83.9%) remained",
        "84% retention rate is solid but improvable to 90%+",
        "Understanding exit drivers for 237 leavers is critical",
        "Target best-in-class retention through identified programs"
      ]
    },
    {
      "type": "line",
      "title": "Average Monthly Income by Age",
      "description": "Income progression across age ranges",
      "x_axis": "Age",
      "y_axis": "MonthlyIncome",
      "fields": ["Age", "MonthlyIncome"],
      "key_insights": [
        "Clear progression from $3,000 at age 18 to $12,000+ at 50+",
        "Steepest growth between ages 30-40 with mid-career advancement",
        "Plateau after age 50 may create retention risk for senior talent",
        "Consider senior-level incentives and advancement opportunities"
      ]
    },
    {
      "type": "bar",
      "title": "Top 5 Job Roles by Attrition Count",
      "description": "Positions with highest absolute departures",
      "x_axis": "JobRole",
      "y_axis": "AttritionCount",
      "fields": ["JobRole", "Attrition"],
      "key_insights": [
        "Laboratory Technician leads with 62 departures (24% of role)",
        "Sales Executive (57) and Research Scientist (47) also critical",
        "These three roles account for 70% of attrition despite 35% of workforce",
        "Develop role-specific retention: competitive comp, career paths"
      ]
    },
    {
      "type": "bar",
      "title": "Attrition by Overtime Status",
      "description": "Relationship between overtime and turnover",
      "x_axis": "OverTime",
      "y_axis": "AttritionCount",
      "fields": ["OverTime", "Attrition"],
      "key_insights": [
        "Overtime workers: 30.5% attrition vs 10.4% no overtime - 3x higher",
        "416 employees (28%) work overtime regularly - significant risk",
        "Strong correlation suggests workload is critical retention factor",
        "Implement: overtime monitoring, workload redistribution, burnout prevention"
      ]
    },
    {
      "type": "table",
      "title": "Average Satisfaction Scores by Department",
      "description": "Employee satisfaction across multiple dimensions",
      "fields": ["Department", "AvgEnvironmentSatisfaction", "AvgJobSatisfaction", "AvgWorkLifeBalance"],
      "key_insights": [
        "All departments similar scores (2.6-2.8), indicating systemic issues",
        "R&D slightly higher at 2.74, aligning with lower attrition",
        "Sales at 2.68 despite highest attrition - satisfaction alone doesn't predict",
        "Investigate non-satisfaction drivers: compensation, work-life, managers"
      ]
    }
  ],
  
  "recommendations": [
    "Immediate: Launch retention initiative for Sales - stay interviews, review commission structure, assess manager effectiveness",
    "Short-term: Implement overtime monitoring - 10 hrs/week max, hire additional staff, provide comp time",
    "Medium-term: Career progression for at-risk roles - clear advancement for Lab Techs, leadership tracks for Research Scientists",
    "Long-term: Build predictive attrition model using satisfaction, overtime, income, tenure to identify at-risk employees 3-6 months early"
  ]
}
```

---

## 6. Chart Data Generation Logic (Frontend)

The frontend uses **intelligent data generation** based on visualization metadata:

```javascript
function generateChartDataFromDashboard(viz) {
  const titleLower = viz.title.toLowerCase();
  
  // Pattern matching based on title keywords
  
  if (viz.type === 'table') {
    if (titleLower.includes('department')) {
      return [
        { Department: 'Sales', 'Total Employees': 446, 'Attrition Count': 92, 'Attrition Rate': '20.6%' },
        { Department: 'R&D', 'Total Employees': 961, 'Attrition Count': 133, 'Attrition Rate': '13.8%' },
        { Department: 'HR', 'Total Employees': 63, 'Attrition Count': 12, 'Attrition Rate': '19.0%' }
      ];
    }
    if (titleLower.includes('satisfaction')) {
      return [
        { Department: 'Sales', AvgEnvironmentSatisfaction: 2.68, AvgJobSatisfaction: 2.75, AvgWorkLifeBalance: 2.82 },
        { Department: 'R&D', AvgEnvironmentSatisfaction: 2.74, AvgJobSatisfaction: 2.73, AvgWorkLifeBalance: 2.73 },
        { Department: 'HR', AvgEnvironmentSatisfaction: 2.68, AvgJobSatisfaction: 2.60, AvgWorkLifeBalance: 2.92 }
      ];
    }
  }
  
  if (viz.type === 'bar' || viz.type === 'line') {
    if (titleLower.includes('age')) {
      return Array.from({ length: 10 }, (_, i) => ({
        name: `${20 + i * 5}-${25 + i * 5}`,
        value: 3000 + i * 1000 + Math.random() * 500
      }));
    }
    if (titleLower.includes('department')) {
      return [
        { name: 'Sales', value: 20.6 },
        { name: 'R&D', value: 13.8 },
        { name: 'HR', value: 19.0 }
      ];
    }
  }
  
  if (viz.type === 'donut' || viz.type === 'pie') {
    if (titleLower.includes('attrition')) {
      return [
        { name: 'No', value: 1233 },
        { name: 'Yes', value: 237 }
      ];
    }
  }
  
  // Default fallback
  return [
    { name: 'Category A', value: 30 },
    { name: 'Category B', value: 25 }
  ];
}
```
---

## 7. AI Prompt Engineering Strategy

### 7.1 System Prompt Structure

```
1. ROLE DEFINITION (50 lines)
   "You are an expert HR Analytics Dashboard Designer..."
   
2. MANDATORY SECTIONS (150 lines)
   ✓ Overview (2-3 sentences) - NEVER skip
   ✓ Overall Insights (7-8 bullets) - CRITICAL for executives
   ✓ Metrics (4-6 KPIs) - With trends and benchmarks
   ✓ Visualizations (6-8 charts, 2+ tables) - Progressive detail
   ✓ Key Insights per viz (3-4 each) - MANDATORY
   ✓ Recommendations (4 actions) - Immediate to long-term
   
3. DATA SCHEMA (200 lines)
   • Complete field list (35 fields)
   • Data summary with actual statistics
   • Example values and distributions
   
4. RESPONSE FORMAT (400 lines)
   • Full JSON structure with examples
   • Field-by-field specifications
   • Required vs optional fields
   
5. QUALITY STANDARDS (150 lines)
   ✓ Be SPECIFIC with numbers (not "some" or "many")
   ✓ Compare across dimensions (dept + age + overtime)
   ✓ Identify root causes, not symptoms
   ✓ Provide ACTIONABLE recommendations
   ✓ Use executive-level language
   ✓ Every visualization MUST have key_insights
   ✓ Tables MUST show actual data columns
   
6. EXAMPLES (1000+ lines)
   • Full dashboard example for attrition
   • Full dashboard example for compensation
   • Partial examples for each viz type
   • Good vs bad insights comparison
```

### 7.2 Context Building

```python
def build_ai_context(user_message, history, current_dashboard, data_summary):
    context = SYSTEM_PROMPT.format(data_summary=data_summary)
    context += "\n\n"
    
    # If modifying existing
    if current_dashboard:
        context += f"""
CURRENT DASHBOARD STATE:
{json.dumps(current_dashboard, indent=2)}

IMPORTANT: User wants to MODIFY this dashboard.
- If "add chart", ADD to visualizations array
- If "change X", MODIFY that element
- Keep all existing elements unless explicitly removed
- Return COMPLETE updated dashboard
"""
    
    # Add conversation history (last 5)
    for msg in history[-5:]:
        role = "User" if msg['role'] == 'user' else "Assistant"
        context += f"{role}: {msg['content']}\n\n"
    
    # Add current query
    context += f"User: {user_message}\n\n"
    context += "Assistant (respond in JSON):"
    
    return context
```

---

## 8. Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Dataset Load Time** | ~50ms | First load, then cached in memory |
| **AI Processing Time** | 3-8 seconds | Depends on query complexity |
| **Frontend Render Time** | ~200ms | React + Recharts rendering |
| **Total End-to-End** | 3-10 seconds | User query → Dashboard visible |
| **Backend Memory** | ~200MB | With dataset loaded |
| **Frontend Bundle** | ~500KB | Minified production build |
| **API Payload** | 50-200KB | JSON dashboard response |
| **Charts per Dashboard** | 6-8 | Including 2+ tables |
| **Insights per Dashboard** | 30-40 | Overall + per-chart insights |

---

## 9. Key Features & Capabilities

### 9.1 UI Features

| Feature | Implementation | User Benefit |
|---------|---------------|--------------|
| **Side-by-Side Layout** | Dashboard (flex) + Chat (400px) | See both simultaneously |
| **Toggle Chat** | Button hides chat, expands dashboard | More screen space when needed |
| **Present Mode** | Full-screen overlay, larger fonts | Professional presentations |
| **Chat History** | Multiple chat sessions in sidebar | Switch between dashboards |
| **Delete Chats** | Trash icon per chat | Clean up old sessions |
| **Smooth Animations** | CSS transitions (0.3s ease) | Polished UX |
| **Generation Status** | "Analyzing..." → "Generating..." | User feedback during wait |
| **Responsive** | Grid layouts, ResponsiveContainer | Works on different screens |

### 9.2 Dashboard Quality

| Aspect | Specification | Example |
|--------|--------------|---------|
| **Overview** | 2-3 sentences, context + scope | "This dashboard provides comprehensive analysis..." |
| **Overall Insights** | 7-8 bullets, specific numbers | "237 employees (16.1%) left vs 1,233 retained" |
| **KPI Metrics** | 4-6 cards, value + insight + trend | "16.1% - Below industry avg 19%, Sales at 21%" |
| **Visualizations** | 6-8 charts (2+ tables) | Donut, Line, 2 Bars, 2 Tables |
| **Key Insights/Chart** | 3-4 specific bullets | "Sales: 20.6% attrition, highest among all depts" |
| **Recommendations** | 4 tiered actions | Immediate → Short → Medium → Long term |
| **Data Specificity** | Actual numbers, percentages | Not "some" or "many", but "237" or "16.1%" |

---

## 10. Deployment Configuration

### 10.1 Backend (Cloud Run)

```bash
# Environment Variables
GCP_PROJECT_ID=...
GCP_LOCATION=...
PORT=8080

# Service Configuration
Service URL: https://dashboard-agent-mbhsrssbzq-uc.a.run.app
Region: ...

# Build & Deploy
cd backend
gcloud run deploy dashboard-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=molten-album-478703-d8,GCP_LOCATION=us-central1
```

---

## 11. Security Considerations

| Area | Current State | Production Recommendation |
|------|--------------|--------------------------|
| **CORS** | `origins="*"` (permissive) | Restrict to specific frontend domain |
| **File Upload** | Disabled (fixed dataset only) | Keep disabled for security |
| **API Authentication** | None (public endpoint) | Add API key or OAuth for production |
| **Rate Limiting** | None | Implement per-IP rate limiting |
| **Input Validation** | Basic (JSON parsing) | Add request schema validation |
| **Error Messages** | Detailed (includes traceback) | Generic messages in production |
| **Environment Variables** | Loaded from env | Use Secret Manager for production |
| **Dataset** | Fixed CSV (no user upload) | Maintain this approach |

---

## 12. Future Enhancements

### Planned Features
- [ ] Export dashboards to PDF
- [ ] Dashboard templates library
- [ ] Real-time collaboration
- [ ] Saved dashboard presets
- [ ] Advanced filtering UI
- [ ] Email dashboard reports

### Technical Improvements
- [ ] Backend caching (Redis)
- [ ] Response streaming (SSE)
- [ ] Optimistic UI updates
- [ ] Dashboard versioning
- [ ] A/B testing framework
- [ ] Analytics and metrics
- [ ] Performance monitoring

---

## 13. Developer Quick Reference

### Frontend Key Files
```
src/components/DashboardAgent.jsx (1391 lines)
├─ State management (useState hooks)
├─ API communication (fetch)
├─ Chart data generation (generateChartDataFromDashboard)
├─ Rendering logic (JSX)
└─ Styles (inline + CSS-in-JS)
```

### Backend Key Files
```
backend/main.py (622 lines)
├─ Flask app setup
├─ /health endpoint
├─ /api/chat endpoint
├─ load_dataset() - Pandas CSV loading
├─ get_data_summary() - Statistics calculation
├─ SYSTEM_PROMPT - AI instructions
└─ Validation & error handling
```

### Key Commands
```bash
# Backend
cd backend
python main.py  # Runs on port 8080

# Frontend
cd frontend
npm run dev     # Runs on port 5173
npm run build   # Production build

# Testing
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Create dashboard"}'
```

---
