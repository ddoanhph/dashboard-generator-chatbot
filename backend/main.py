from flask import Flask, request, jsonify
from flask_cors import CORS
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import os
import json
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "molten-album-478703-d8")
LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Gemini model
#model = GenerativeModel("gemini-2.5-pro")
model = GenerativeModel("gemini-2.0-flash-001")

# Data file path/currently instead of use cloud storage, just load the data with file path
# Solution when scale would involve the connection with myPulse (which is uncertain)
DATA_FILE = 'data/WA_Fn-UseC_-HR-Employee-Attrition.csv'

def load_dataset():
    try:
        df = pd.read_csv(DATA_FILE)
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def get_data_summary():
    """Get comprehensive summary statistics from the dataset"""
    df = load_dataset()
    if df is None:
        return "Dataset not available."
    
    # key statistics
    total_employees = len(df)
    attrition_yes = len(df[df['Attrition'] == 'Yes'])
    attrition_no = len(df[df['Attrition'] == 'No'])
    attrition_rate = (attrition_yes / total_employees * 100) if total_employees > 0 else 0
    
    # Demographics
    avg_age = df['Age'].mean()
    gender_dist = df['Gender'].value_counts().to_dict()
    
    # Job info
    departments = df['Department'].value_counts().to_dict()
    job_roles = df['JobRole'].value_counts().to_dict()
    
    # Compensation
    avg_income = df['MonthlyIncome'].mean()
    median_income = df['MonthlyIncome'].median()
    
    # Satisfaction metrics
    avg_job_satisfaction = df['JobSatisfaction'].mean()
    avg_env_satisfaction = df['EnvironmentSatisfaction'].mean()
    avg_work_life_balance = df['WorkLifeBalance'].mean()
    
    # Tenure
    avg_years_company = df['YearsAtCompany'].mean()
    avg_total_working_years = df['TotalWorkingYears'].mean()
    
    summary = f"""
DATASET SUMMARY:
Total Records: {total_employees}
Attrition: {attrition_yes} Yes ({attrition_rate:.2f}%), {attrition_no} No ({100-attrition_rate:.2f}%)

DEMOGRAPHICS:
- Average Age: {avg_age:.1f} years
- Gender: {json.dumps(gender_dist)}

DEPARTMENTS & ROLES:
- Departments: {json.dumps(departments)}
- Top Job Roles: {json.dumps(dict(list(job_roles.items())[:5]))}

COMPENSATION:
- Average Monthly Income: ${avg_income:,.0f}
- Median Monthly Income: ${median_income:,.0f}

SATISFACTION METRICS (1-4 scale):
- Job Satisfaction: {avg_job_satisfaction:.2f}
- Environment Satisfaction: {avg_env_satisfaction:.2f}
- Work-Life Balance: {avg_work_life_balance:.2f}

TENURE:
- Average Years at Company: {avg_years_company:.1f}
- Average Total Working Years: {avg_total_working_years:.1f}

OVERTIME:
- Employees Working Overtime: {len(df[df['OverTime'] == 'Yes'])} ({len(df[df['OverTime'] == 'Yes'])/total_employees*100:.1f}%)
"""
    return summary

# Enhanced system prompt for professional dashboards
# This should be updated for more concise/on point
SYSTEM_PROMPT = """You are an expert HR Analytics Dashboard Designer and Data Analyst specializing in employee attrition analysis.
CRITICAL: You MUST include ALL sections below in EVERY response. Do not skip any section.
Your role is to create COMPREHENSIVE, PROFESSIONAL dashboards following this EXACT structure:

1. OVERVIEW SECTION (MANDATORY - 2-3 sentences)
   - Context about what this dashboard analyzes
   - Purpose and key business questions addressed
   - Scope of analysis
   - NEVER skip this section

2. OVERALL INSIGHTS (MANDATORY - 7-8 bullet points)
   - High-level executive summary with specific numbers
   - Major trends and patterns discovered in the data
   - Critical findings that require immediate attention
   - Comparative analysis across dimensions
   - Root cause indicators
   - Strategic implications for HR leadership
   - Risk areas and opportunities
   - Next steps or recommendations
   - NEVER skip this section - it's crucial for executives

3. METRICS (MANDATORY - 4-6 KPI cards)
   - Primary KPIs with actual calculated values
   - Context, benchmarks, and industry comparisons
   - Trend indicators (up/down/stable)
   - Brief insight for each metric

4. VISUALIZATIONS (MANDATORY - 6-8 charts including TABLES)
   - MUST include at least 2 TABLE visualizations for detailed breakdowns
   - Mix of chart types: bar, line, pie, donut, and TABLES
   - Each with clear, descriptive title
   - Detailed description of what the chart shows
   - Progressive detail: start with high-level, drill into specifics
   - Use actual field names from the dataset
   
   REQUIRED TABLE EXAMPLES:
   - Attrition Rate by Department (table with columns: Department, Total Employees, Attrition Count, Attrition Rate)
   - Top Job Roles by Attrition Count (table with columns: JobRole, Attrition, Count)
   - Satisfaction Scores by Department (table with multiple satisfaction metrics)

5. KEY INSIGHTS (MANDATORY - 3-4 insights per visualization)
   - Specific insights derived from each chart
   - Actionable recommendations
   - Root cause analysis where applicable
   - Compare segments and identify outliers
   - Business impact assessment
   - EVERY visualization MUST have key_insights array populated

DATA SCHEMA AND AVAILABLE FIELDS:
{data_summary}

COMPLETE FIELD LIST:
- Age, Attrition, BusinessTravel, DailyRate, Department, DistanceFromHome
- Education, EducationField, EmployeeCount, EmployeeNumber, EnvironmentSatisfaction
- Gender, HourlyRate, JobInvolvement, JobLevel, JobRole, JobSatisfaction
- MaritalStatus, MonthlyIncome, MonthlyRate, NumCompaniesWorked, Over18, OverTime
- PercentSalaryHike, PerformanceRating, RelationshipSatisfaction, StandardHours
- StockOptionLevel, TotalWorkingYears, TrainingTimesLastYear, WorkLifeBalance
- YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, YearsWithCurrManager

RESPONSE FORMAT (MUST BE VALID JSON - ALL FIELDS REQUIRED):
{{
  "message": "Brief response acknowledging the user's request",
  "analysis_type": "attrition|compensation|satisfaction|demographics|tenure|custom",
  "dashboard": {{
    "title": "Clear, Professional Dashboard Title",
    "overview": "REQUIRED: 2-3 sentence paragraph providing context and scope of this analysis. Explain what business questions this addresses and why it matters to HR leadership.",
    "overall_insights": [
      "REQUIRED: Insight 1 with specific numbers (e.g., '237 employees or 16.1% have left')",
      "REQUIRED: Insight 2 comparing segments (e.g., 'Sales at 21% vs R&D at 14%')",
      "REQUIRED: Insight 3 identifying trends (e.g., 'Attrition concentrated at Job Level 1')",
      "REQUIRED: Insight 4 highlighting risks (e.g., 'Overtime workers show 3x higher attrition')",
      "REQUIRED: Insight 5 with opportunity (e.g., 'High satisfaction correlates with retention')",
      "REQUIRED: Insight 6 showing correlation (e.g., 'Income growth reduces attrition risk')",
      "REQUIRED: Insight 7 with recommendation (e.g., 'Focus retention on Lab Technician role')",
      "REQUIRED: Insight 8 with next steps (e.g., 'Conduct exit interviews for Sales department')"
    ],
    "metrics": [
      {{
        "label": "Overall Attrition Rate",
        "value": "16.1%",
        "insight": "Below industry average of 19%, but Sales department at 21% requires attention",
        "trend": "stable",
        "benchmark": "Industry: 19% | Best-in-class: 12%"
      }},
      {{
        "label": "Average Monthly Income",
        "value": "$6,503",
        "insight": "Competitive but shows 15% variance across departments",
        "trend": "up",
        "benchmark": "Market median: $6,200"
      }}
    ],
    "visualizations": [
      {{
        "type": "table",
        "title": "Attrition Rate by Department",
        "description": "Detailed breakdown of employee turnover across all departments showing total headcount, attrition count, and percentage rates to identify high-risk areas",
        "fields": ["Department", "Total Employees", "Attrition Count", "Attrition Rate"],
        "key_insights": [
          "REQUIRED: Sales has highest attrition at 20.6% (92 of 446 employees), significantly above company average",
          "REQUIRED: R&D shows strong retention at 13.8% (133 of 961), best performing department",
          "REQUIRED: HR at 19.0% aligns with company average but small sample size (12 of 63)",
          "REQUIRED: Immediate action needed: Implement retention program for Sales, study R&D best practices"
        ]
      }},
      {{
        "type": "bar",
        "title": "Top 5 Job Roles by Attrition Count",
        "description": "Identifies specific positions with highest absolute number of departures to prioritize retention efforts and resource allocation",
        "x_axis": "JobRole",
        "y_axis": "AttritionCount",
        "fields": ["JobRole", "Attrition"],
        "key_insights": [
          "REQUIRED: Laboratory Technician leads with 62 departures, representing 24% of the role",
          "REQUIRED: Sales Executive (57) and Research Scientist (47) also show critical loss rates",
          "REQUIRED: These three roles account for 70% of total attrition despite being 35% of workforce",
          "REQUIRED: Develop role-specific retention: competitive comp for Lab Tech, career paths for Research Scientists"
        ]
      }},
      {{
        "type": "line",
        "title": "Average Monthly Income by Age",
        "description": "Income progression across age ranges showing compensation growth patterns and potential pay equity issues",
        "x_axis": "Age",
        "y_axis": "MonthlyIncome",
        "fields": ["Age", "MonthlyIncome"],
        "key_insights": [
          "REQUIRED: Clear progression from $3,000 at age 18 to $12,000+ for 50+ employees",
          "REQUIRED: Steepest growth between ages 30-40 coinciding with mid-career advancement",
          "REQUIRED: Plateau after age 50 may create retention risk for experienced senior talent",
          "REQUIRED: Consider implementing senior-level incentives and continued advancement opportunities"
        ]
      }},
      {{
        "type": "donut",
        "title": "Attrition Rate Distribution",
        "description": "Overall employee retention showing proportion of employees who left versus those who remained",
        "fields": ["Attrition"],
        "key_insights": [
          "REQUIRED: 237 employees (16.1%) left while 1,233 (83.9%) remained with company",
          "REQUIRED: 84% retention rate is solid but leaves room for improvement to best-in-class",
          "REQUIRED: Understanding exit drivers for 237 leavers is critical to prevent future attrition",
          "REQUIRED: Target 90%+ retention through programs identified in other visualizations"
        ]
      }},
      {{
        "type": "bar",
        "title": "Attrition by Overtime Status",
        "description": "Analyzes relationship between overtime work and turnover to assess work-life balance impact on retention",
        "x_axis": "OverTime",
        "y_axis": "AttritionCount",
        "fields": ["OverTime", "Attrition"],
        "key_insights": [
          "REQUIRED: Overtime workers show 30.5% attrition vs 10.4% for no overtime - nearly 3x higher",
          "REQUIRED: 416 employees (28%) work overtime regularly, creating significant retention risk",
          "REQUIRED: Strong correlation suggests workload management is critical retention factor",
          "REQUIRED: Implement: overtime monitoring, workload redistribution, manager training on burnout prevention"
        ]
      }},
      {{
        "type": "table",
        "title": "Average Satisfaction Scores by Department",
        "description": "Compares employee satisfaction across multiple dimensions to identify morale issues and their correlation with attrition",
        "fields": ["Department", "AvgEnvironmentSatisfaction", "AvgJobSatisfaction", "AvgWorkLifeBalance"],
        "key_insights": [
          "REQUIRED: All departments show similar scores (2.6-2.8 on 4-point scale), indicating systemic rather than departmental issues",
          "REQUIRED: R&D slightly higher at 2.74, aligning with their lower attrition rate",
          "REQUIRED: Sales at 2.68 despite highest attrition suggests satisfaction scores alone don't predict turnover",
          "REQUIRED: Investigate non-satisfaction drivers in Sales: compensation structure, work-life balance, manager quality"
        ]
      }}
    ],
    "recommendations": [
      "Immediate: Launch comprehensive retention initiative for Sales department - conduct stay interviews with top performers, review commission structure competitiveness, assess manager effectiveness and provide coaching",
      "Short-term: Implement overtime monitoring and workload balancing program - set maximum overtime thresholds (10 hrs/week), hire additional staff for high-OT roles, provide comp time or bonuses for required overtime",
      "Medium-term: Develop targeted career progression paths for at-risk roles - clear advancement criteria and timelines for Lab Technicians, research opportunities and leadership tracks for Research Scientists",
      "Long-term: Build predictive attrition model using satisfaction scores, overtime hours, income levels, and tenure data to identify at-risk employees 3-6 months before departure and intervene proactively"
    ]
  }}
}}

CRITICAL QUALITY STANDARDS - NON-NEGOTIABLE:
✓ NEVER skip overview, overall_insights, or key_insights - these are MANDATORY
✓ ALWAYS include at least 2 table visualizations for detailed breakdowns
✓ Be SPECIFIC with numbers, percentages, and counts from actual data
✓ Compare metrics across segments (departments, age groups, roles, overtime status)
✓ Identify root causes and correlations, not just surface symptoms
✓ Provide ACTIONABLE recommendations tied to business impact
✓ Use professional, executive-level language suitable for C-suite presentation
✓ Cross-reference multiple dimensions (e.g., "Sales with overtime has 35% attrition")
✓ Every insight must be supported by data and lead to a recommendation
✓ Calculate actual percentages and rates from the data fields
✓ Use field names exactly as they appear in the dataset
✓ EVERY visualization MUST have 3-4 key insights populated
✓ Tables MUST show actual data columns and meaningful comparisons

VISUALIZATION BEST PRACTICES:
- Start with overview charts (overall attrition, distribution)
- Include detailed TABLES for department and role breakdowns
- Drill into dimensions (by department, by age, by role, by overtime)
- Include correlation analysis (overtime vs attrition, income vs satisfaction)
- End with actionable insights and specific recommendations
- Each chart must tell a story and lead to action
- Tables are ESSENTIAL for executive decision-making
"""


@app.route('/health', methods=['GET'])
def health_check():
    df = load_dataset()
    return jsonify({
        "status": "healthy",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "model": "gemini-2.5-pro (Vertex AI)",
        "dataset_loaded": df is not None,
        "records": len(df) if df is not None else 0,
        "data_file": DATA_FILE
    }), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        current_dashboard = data.get('current_dashboard', None)
        
        # Get data summary
        data_summary = get_data_summary()
        
        # Build context with data summary
        context = SYSTEM_PROMPT.format(data_summary=data_summary) + "\n\n"
        
        # If modifying existing dashboard
        if current_dashboard:
            context += f"""
CURRENT DASHBOARD STATE:
{json.dumps(current_dashboard, indent=2)}

IMPORTANT: User wants to MODIFY this existing dashboard.
- If they say "add a chart", ADD to visualizations array
- If they say "change X", MODIFY that specific element
- Keep all existing elements unless explicitly asked to remove
- Return the COMPLETE updated dashboard with all sections
"""
        
        # Add conversation history
        for msg in conversation_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['content']}\n\n"
        
        context += f"User: {user_message}\n\nAssistant (respond in valid JSON format only):"
        
        # Call Gemini
        response = model.generate_content(
            context,
            generation_config={
                "max_output_tokens": 8192,  # Increased for comprehensive dashboards
                "temperature": 0.3,  # Lower for consistency
                "top_p": 0.9,
            }
        )
        
        assistant_message = response.text
        
        # Parse JSON
        try:
            # Clean up markdown code blocks if present
            if "```json" in assistant_message:
                json_start = assistant_message.find("```json") + 7
                json_end = assistant_message.find("```", json_start)
                assistant_message = assistant_message[json_start:json_end].strip()
            elif "```" in assistant_message:
                json_start = assistant_message.find("```") + 3
                json_end = assistant_message.find("```", json_start)
                assistant_message = assistant_message[json_start:json_end].strip()
            
            dashboard_data = json.loads(assistant_message)
        except Exception as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {assistant_message}")
            dashboard_data = {
                "message": "I've generated insights, but had trouble formatting. Please try again.",
                "dashboard": current_dashboard,
                "error": str(e)
            }
        
        return jsonify({
            "response": dashboard_data.get("message", assistant_message),
            "dashboard": dashboard_data.get("dashboard"),
            "analysis_type": dashboard_data.get("analysis_type"),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "message": "An error occurred while processing your request."
        }), 500


@app.route('/api/data/summary', methods=['GET'])
def get_summary():
    """Endpoint to get dataset summary"""
    try:
        summary = get_data_summary()
        return jsonify({
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
