import streamlit as st
import re
import json
import google.generativeai as genai
import plotly.graph_objects as go

# ------------------------------------------------------------
# Configure your Google Generative AI API key once at the start
# ------------------------------------------------------------
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
genai.configure(api_key=GOOGLE_API_KEY)

# We'll reference this model for all calls:
GEMINI_MODEL = "gemini-2.0-flash"

# ------------------------------------------------------------
# Custom CSS (upgraded for world-class aesthetics)
# ------------------------------------------------------------
custom_css = """
<style>
/* Use the Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* Base styles */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1a202c;
    -webkit-font-smoothing: antialiased;
}

/* Overall page background with enhanced subtle gradient */
.main {
    background: linear-gradient(145deg, #f8fafc 0%, #edf2f7 100%);
}

/* Headings with improved typography */
h1 {
    font-weight: 800;
    font-size: 2.75rem;
    letter-spacing: -0.025em;
    color: #1a202c;
    line-height: 1.1;
    margin-bottom: 1.25rem;
}

h2 {
    font-weight: 700;
    font-size: 2rem;
    letter-spacing: -0.025em;
    color: #2d3748;
    margin-top: 1.75rem;
    margin-bottom: 1rem;
}

h3 {
    font-weight: 600;
    font-size: 1.5rem;
    color: #4a5568;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

h4 {
    font-weight: 600;
    font-size: 1.2rem;
    color: #4a5568;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}

p {
    font-size: 1.05rem;
    line-height: 1.7;
    color: #4a5568;
    margin-bottom: 1.25rem;
}

/* Sidebar styling with enhanced depth */
[data-testid="stSidebar"] {
    background-color: #fff;
    border-right: 1px solid #e2e8f0;
    box-shadow: 2px 0px 10px rgba(0, 0, 0, 0.03);
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding-top: 2.25rem;
    padding-left: 1.75rem;
    padding-right: 1.75rem;
}
[data-testid="stSidebar"] h1 {
    font-size: 1.6rem;
    color: #5a67d8;
    margin-bottom: 2.25rem;
}

/* Custom form inputs with refined styling */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] {
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    padding: 0.85rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    width: 100%;
    margin-bottom: 1.25rem;
    font-size: 1.05rem;
    transition: all 0.2s ease-in-out;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #5a67d8;
    box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.15);
    transform: translateY(-1px);
}

/* More sophisticated button styling */
[data-testid="baseButton-secondary"], 
.stButton button {
    background: linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.75rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.025em !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 10px rgba(76, 29, 149, 0.3), 0 1px 3px rgba(76, 29, 149, 0.2) !important;
}
[data-testid="baseButton-secondary"]:hover, 
.stButton button:hover {
    background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 14px rgba(124, 58, 237, 0.35), 0 3px 6px rgba(124, 58, 237, 0.2) !important;
}
[data-testid="baseButton-secondary"]:active, 
.stButton button:active {
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 6px rgba(124, 58, 237, 0.2), 0 1px 3px rgba(124, 58, 237, 0.1) !important;
}

/* Enhanced card styling with better transitions */
.card {
    background-color: white;
    border-radius: 14px;
    padding: 1.75rem;
    margin-bottom: 1.75rem;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.06), 0 10px 20px rgba(0, 0, 0, 0.035);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid #f0f4f8;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08), 0 20px 40px rgba(0, 0, 0, 0.04);
}

/* Landing page title styling with enhanced gradient */
.landing-title {
    font-size: 3.75rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6D28D9 0%, #4338CA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.75rem;
    letter-spacing: -0.05em;
    line-height: 1;
    text-align: center;
}
.landing-subtitle {
    font-size: 1.35rem;
    font-weight: 500;
    color: #4a5568;
    margin-bottom: 2.25rem;
    text-align: center;
}

/* Logo styling with refined depth */
.logo {
    display: flex;
    align-items: center;
    margin-bottom: 2.25rem;
}
.logo-icon {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #6D28D9 0%, #4338CA 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.85rem;
    color: white;
    font-weight: 700;
    font-size: 1.35rem;
    box-shadow: 0 4px 8px rgba(76, 29, 149, 0.25);
}
.logo-text {
    font-size: 1.6rem;
    font-weight: 800;
    color: #5a67d8;
}

/* Section headers with improved visuals */
.section-header {
    display: flex;
    align-items: center;
    margin-bottom: 1.75rem;
    padding-bottom: 0.85rem;
    border-bottom: 1px solid #e2e8f0;
}
.section-icon {
    width: 36px;
    height: 36px;
    background: #EBF4FF;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.85rem;
    color: #5a67d8;
    font-weight: 700;
    font-size: 1.15rem;
}

/* Decision box with enhanced visual appeal */
.decision-box {
    background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
    border-radius: 16px;
    padding: 2.25rem 1.75rem;
    margin-top: 2.25rem;
    margin-bottom: 2.25rem;
    border: 1px solid #f0f4f8;
    box-shadow: 0 15px 35px rgba(76, 29, 149, 0.15), 0 5px 15px rgba(76, 29, 149, 0.08);
    text-align: center;
    animation: fadeInUp 0.6s ease-out forwards;
    transform: translateY(20px);
    opacity: 0;
}
.decision-box h2 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6D28D9 0%, #4338CA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.75rem;
}
.decision-box .score {
    font-size: 3.5rem;
    font-weight: 900;
    color: #6D28D9;
    margin: 1.25rem 0;
    text-shadow: 0 2px 5px rgba(109, 40, 217, 0.25);
}
.recommendation {
    margin-top: 1.25rem;
    font-size: 1.5rem;
    font-weight: 700;
}
.recommendation.positive {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.recommendation.negative {
    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.recommendation.neutral {
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Factor cards with improved visuals */
.factor-card {
    display: flex;
    align-items: center;
    background-color: white;
    border-radius: 12px;
    padding: 1.15rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.03);
    transition: all 0.25s ease;
    border-left: 4px solid #6D28D9;
}
.factor-card:hover {
    box-shadow: 0 5px 10px rgba(0, 0, 0, 0.08);
    transform: translateX(3px);
}
.factor-card .factor-letter {
    font-size: 1.35rem;
    font-weight: 800;
    color: #6D28D9;
    margin-right: 1.15rem;
    width: 2.25rem;
    height: 2.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #EBF4FF;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(76, 29, 149, 0.15);
}
.factor-card .factor-description {
    flex: 1;
    font-size: 1.05rem;
    line-height: 1.5;
}
.factor-card .factor-value {
    font-size: 1.35rem;
    font-weight: 800;
    margin-left: auto;
    padding-left: 1rem;
}
.factor-card .factor-value.positive {
    color: #10B981;
}
.factor-card .factor-value.negative {
    color: #EF4444;
}
.factor-card .factor-value.neutral {
    color: #A0AEC0;
}

/* Item card styles with enhanced depth */
.item-card {
    background: white;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.03);
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    transition: all 0.25s ease;
}
.item-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04);
}
.item-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #EBF4FF 0%, #C7D2FE 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 1.25rem;
    color: #6D28D9;
    font-weight: 700;
    font-size: 1.5rem;
    box-shadow: 0 2px 5px rgba(76, 29, 149, 0.1);
}
.item-details {
    flex: 1;
}
.item-name {
    font-weight: 700;
    font-size: 1.25rem;
    color: #2d3748;
}
.item-cost {
    font-weight: 800;
    font-size: 1.35rem;
    background: linear-gradient(135deg, #6D28D9 0%, #4338CA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Inferred data box with refined styling */
.inferred-data {
    background-color: #F9FAFB;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-top: 1.25rem;
    margin-bottom: 1.5rem;
    border: 1px dashed #CBD5E0;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.03);
}
.inferred-data h4 {
    font-size: 1.15rem;
    font-weight: 700;
    color: #4a5568;
    margin-bottom: 0.85rem;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 0.5rem;
}
.inferred-item {
    display: flex;
    align-items: center;
    margin-bottom: 0.65rem;
}
.inferred-label {
    font-weight: 600;
    min-width: 200px;
    color: #4a5568;
    font-size: 1.05rem;
}
.inferred-value {
    color: #2d3748;
    font-weight: 500;
    font-size: 1.05rem;
}

/* Input Form Container with enhanced depth */
.input-form-container {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 2.25rem 2rem;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.07), 0 5px 15px rgba(0, 0, 0, 0.05);
    margin-bottom: 2.25rem;
    border: 1px solid #f0f4f8;
    position: relative;
    overflow: hidden;
}

.input-form-container::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 5px;
    background: linear-gradient(90deg, #6D28D9, #4338CA);
}

.main-input-field input {
    font-size: 1.15rem;
    padding: 1.15rem;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 3px 5px rgba(0, 0, 0, 0.03);
    transition: all 0.3s ease;
}

.main-input-field input:focus {
    border-color: #6D28D9;
    box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.15);
    transform: translateY(-2px);
}

.submit-button .stButton button {
    background: linear-gradient(135deg, #6D28D9 0%, #4338CA 100%) !important;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.95rem 1.75rem;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.025em;
    box-shadow: 0 5px 15px rgba(109, 40, 217, 0.35);
    transition: all 0.3s ease;
}

.submit-button .stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(109, 40, 217, 0.4);
}

.cost-field input {
    font-size: 1.15rem;
    text-align: center;
    font-weight: 600;
}

.form-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: center;
}

.form-header-icon {
    margin-right: 0.85rem;
    font-size: 1.6rem;
}

/* App Header with enhanced typography */
.app-header {
    text-align: center;
    padding-bottom: 1.75rem;
    margin-bottom: 2.25rem;
}

.app-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6D28D9 0%, #4338CA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.65rem;
    letter-spacing: -0.03em;
}

.app-subtitle {
    font-size: 1.35rem;
    color: #4a5568;
    font-weight: 500;
    max-width: 650px;
    margin: 0 auto;
    line-height: 1.5;
}

/* How it works page with enhanced visuals */
.how-it-works-container {
    background: #F9FAFB;
    border-radius: 16px;
    padding: 2.5rem;
    margin-top: 2.25rem;
    margin-bottom: 2.25rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05), 0 5px 15px rgba(0, 0, 0, 0.03);
}
.how-it-works-container h2 {
    background: linear-gradient(135deg, #6D28D9 0%, #4338CA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.25rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
}
.how-it-works-container p {
    font-size: 1.15rem;
    line-height: 1.7;
    margin-bottom: 1.25rem;
    color: #2d3748;
}
.how-it-works-container ul {
    list-style-type: none;
    margin-left: 0.5rem;
    margin-bottom: 1.5rem;
    color: #2d3748;
}
.how-it-works-container ul li {
    position: relative;
    padding-left: 2rem;
    margin-bottom: 1rem;
    font-size: 1.15rem;
    line-height: 1.6;
}
.how-it-works-container ul li:before {
    content: "•";
    color: #6D28D9;
    font-weight: bold;
    font-size: 1.5rem;
    position: absolute;
    left: 0.5rem;
    top: -0.25rem;
}

/* Analysis in progress animation */
.analysis-in-progress {
    padding: 1rem;
    border-radius: 12px;
    background: #F9FAFB;
    margin-bottom: 1.5rem;
    text-align: center;
    animation: pulse 2s infinite;
}

/* Enhanced animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(109, 40, 217, 0.2);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(109, 40, 217, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(109, 40, 217, 0);
    }
}

/* Quick Results Box */
.quick-results-box {
    background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
    border-radius: 14px;
    padding: 1.5rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    justify-content: space-between;
    animation: fadeInUp 0.5s ease-out forwards;
}

.quick-results-label {
    font-weight: 700;
    font-size: 1.2rem;
    color: #2d3748;
}

.quick-results-value {
    font-weight: 800;
    font-size: 1.4rem;
    padding: 0.5rem 1.25rem;
    border-radius: 8px;
}

.quick-results-value.positive {
    background: #10B981;
    color: white;
}

.quick-results-value.negative {
    background: #EF4444;
    color: white;
}

.quick-results-value.neutral {
    background: #F59E0B;
    color: white;
}

/* Chart containers */
.chart-container {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.75rem;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    border: 1px solid #f0f4f8;
}

.chart-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 1rem;
    text-align: center;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def render_logo():
    st.markdown("""
    <div class="logo">
        <div class="logo-icon">M</div>
        <div class="logo-text">Munger AI</div>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title, icon):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon">{icon}</div>
        <h2>{title}</h2>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Radar / Gauge Charts
# ------------------------------------------------------------
def create_radar_chart(factors):
    import plotly.graph_objects as go
    categories = ['Discretionary Income','Opportunity Cost','Goal Alignment','Long-Term Impact','Behavioral']
    vals = [factors['D'], factors['O'], factors['G'], factors['L'], factors['B']]
    # Close the shape
    vals.append(vals[0])
    categories.append(categories[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=categories,
        fill='toself',
        fillcolor='rgba(109, 40, 217, 0.2)',
        line=dict(color='#6D28D9', width=2),
        name='Factors'
    ))
    # Reference lines
    for i in [-2, -1, 0, 1, 2]:
        fig.add_trace(go.Scatterpolar(
            r=[i]*len(categories),
            theta=categories,
            line=dict(color='rgba(200,200,200,0.5)', width=1, dash='dash'),
            showlegend=False
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[-3, 3],
                tickvals=[-2, -1, 0, 1, 2],
                gridcolor='rgba(200, 200, 200, 0.3)'
            ),
            angularaxis=dict(gridcolor='rgba(200, 200, 200, 0.3)'),
            bgcolor='rgba(255,255,255,0.9)'
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=20, b=20),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_pds_gauge(pds):
    import plotly.graph_objects as go
    # Color logic
    if pds >= 5:
        color = "#10B981"  # green
    elif pds < 0:
        color = "#EF4444"  # red
    else:
        color = "#F59E0B"  # orange
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pds,
        domain={'x': [0,1], 'y': [0,1]},
        gauge={
            'axis': {'range': [-10,10], 'tickwidth': 1, 'tickcolor': "#2D3748"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [-10,0], 'color': '#FEE2E2'},
                {'range': [0,5], 'color': '#FEF3C7'},
                {'range': [5,10], 'color': '#D1FAE5'}
            ],
            'threshold': {
                'line': {'color': "#6D28D9", 'width': 2},
                'thickness': 0.8,
                'value': 5
            }
        },
        title={'text': "Purchase Decision Score", 'font': {'size': 18, 'color': "#2D3748", 'family': "Inter, sans-serif"}},
        number={'font': {'size': 40, 'color': color, 'family': "Inter, sans-serif"}, 'suffix': "", 'prefix': ('+' if pds > 0 else '')}
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#2D3748", 'family': "Inter, sans-serif"}
    )
    return fig

# ------------------------------------------------------------
# AI Utility Functions
# ------------------------------------------------------------
def infer_purchase_details(item_name, item_cost):
    import google.generativeai as genai
    prompt = f"""
You are a financial advisor AI that needs to infer details about a purchase decision.
Based only on the item name and cost, infer reasonable values for:
1. Monthly leftover income
2. Whether the buyer likely has high-interest debt (Yes/No)
3. The buyer's main financial goal
4. Purchase urgency (Urgent Needs/Mostly Wants/Mixed)

Item: "{item_name}"
Cost: ${item_cost:.2f}

Provide your response in valid JSON format only:
{{
  "leftover_income": 2000,
  "has_high_interest_debt": "Yes",
  "main_financial_goal": "Save for retirement",
  "purchase_urgency": "Mostly Wants"
}}
"""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(
            prompt, 
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=512
            )
        )
        if not resp:
            st.error("No response from Gemini.")
            return default_inferences(item_cost)
        text = resp.text
        # Attempt to parse JSON
        candidates = re.findall(r"(\{[\s\S]*?\})", text)
        for c in candidates:
            try:
                data = json.loads(c)
                needed = ["leftover_income", "has_high_interest_debt","main_financial_goal","purchase_urgency"]
                if all(k in data for k in needed):
                    return data
            except:
                pass
        st.error("Unable to parse valid JSON for purchase details.")
        return default_inferences(item_cost)
    except Exception as e:
        st.error(f"Error calling Gemini: {e}")
        return default_inferences(item_cost)

def default_inferences(cost):
    leftover = max(1000, cost*2)
    return {
        "leftover_income": leftover,
        "has_high_interest_debt": "No",
        "main_financial_goal": "Save for emergencies",
        "purchase_urgency": "Mixed"
    }

def get_factors_from_gemini(leftover_income, has_high_interest_debt,
                            main_financial_goal, purchase_urgency,
                            item_name, item_cost):
    import google.generativeai as genai
    prompt = f"""
We have a Purchase Decision Score (PDS) formula:
PDS = D + O + G + L + B (each factor between -2 and 2).

Guidelines:
1. D: Higher if leftover_income >> item_cost
2. O: Positive if no high-interest debt, negative if debt
3. G: Positive if aligns with main goal, negative if conflicts
4. L: Positive if long-term benefit, negative if extra cost
5. B: Positive if truly urgent, negative if impulsive want

Evaluate:
- Item: {item_name}
- Cost: {item_cost}
- leftover_income: {leftover_income}
- high_interest_debt: {has_high_interest_debt}
- main_financial_goal: {main_financial_goal}
- purchase_urgency: {purchase_urgency}

Return valid JSON:
{{
  "D": -2 to 2,
  "O": -2 to 2,
  "G": -2 to 2,
  "L": -2 to 2,
  "B": -2 to 2,
  "D_explanation": "...",
  "O_explanation": "...",
  "G_explanation": "...",
  "L_explanation": "...",
  "B_explanation": "..."
}}
"""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=512
            )
        )
        if not resp:
            st.error("No response from Gemini.")
            return {"D":0,"O":0,"G":0,"L":0,"B":0}
        text = resp.text
        # Attempt parse
        candidates = re.findall(r"(\{[\s\S]*?\})", text)
        for c in candidates:
            try:
                data = json.loads(c)
                if all(f in data for f in ["D","O","G","L","B"]):
                    return data
            except:
                pass
        st.error("Unable to parse valid JSON for factors.")
        return {"D":0,"O":0,"G":0,"L":0,"B":0}
    except Exception as e:
        st.error(f"Error calling Gemini: {e}")
        return {"D":0,"O":0,"G":0,"L":0,"B":0}

def compute_pds(factors):
    return sum(factors.get(f,0) for f in ["D","O","G","L","B"])

def get_recommendation(pds):
    if pds >= 5:
        return "Buy it.", "positive"
    elif pds < 0:
        return "Don't buy it.", "negative"
    else:
        return "Consider carefully.", "neutral"

# ------------------------------------------------------------
# Rendering Helpers
# ------------------------------------------------------------
def render_item_card(item_name, cost):
    icon = "💼" if cost >= 1000 else "🛍️"
    st.markdown(f"""
    <div class="item-card">
        <div class="item-icon">{icon}</div>
        <div class="item-details">
            <div class="item-name">{item_name}</div>
        </div>
        <div class="item-cost">${cost:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

def render_inferred_data(data_dict):
    st.markdown("<div class='inferred-data'><h4>AI-Inferred Data</h4>", unsafe_allow_html=True)
    for k,v in data_dict.items():
        st.markdown(f"""
        <div class="inferred-item">
            <div class="inferred-label">{k}:</div>
            <div class="inferred-value">{v}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def render_factor_card(factor, value, desc):
    # color class
    if value > 0:
        val_class = "positive"
    elif value < 0:
        val_class = "negative"
    else:
        val_class = "neutral"
    st.markdown(f"""
    <div class="factor-card">
        <div class="factor-letter">{factor}</div>
        <div class="factor-description">{desc}</div>
        <div class="factor-value {val_class}">{value:+d}</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Main Application
# ------------------------------------------------------------
def main():
    # Sidebar
    with st.sidebar:
        render_logo()
        st.markdown("##### Decision Assistant")
        pages = ["Decision Tool", "How It Works"]
        choice = st.radio("", pages, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### Quick Tips")
        st.markdown("""
        - Enter the item name and cost.
        - Our AI infers key financial details.
        - A higher score suggests a sound purchase.
        - Score above 5 means it's a buy.
        """)
        
        st.markdown("---")
        st.markdown("© 2025 Munger AI")
    
    # Main title (visible on all pages)
    st.markdown("""
    <div class="app-header">
        <div class="app-title">Munger AI</div>
        <div class="app-subtitle">Should you buy it? Our AI decides in seconds.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # Decision Tool
    # ---------------------------------------------------------
    if choice == "Decision Tool":
        st.header("Decision Tool")
        with st.form("decision_form", clear_on_submit=True):
            item_name = st.text_input("Enter the item name:")
            item_cost = st.number_input("Enter the cost of the item:", min_value=0.0, format="%.2f")
            submit = st.form_submit_button("Should I Buy It?")
        
        if submit:
            if item_name and item_cost > 0:
                st.subheader("Analyzing your decision...")
                with st.spinner("Letting the AI think..."):
                    # Render the item card (item description)
                    render_item_card(item_name, item_cost)
                    
                    # Compute AI inferences and evaluation factors
                    inferences = infer_purchase_details(item_name, item_cost)
                    factors = get_factors_from_gemini(
                        inferences["leftover_income"],
                        inferences["has_high_interest_debt"],
                        inferences["main_financial_goal"],
                        inferences["purchase_urgency"],
                        item_name,
                        item_cost
                    )
                    pds = compute_pds(factors)
                    recommendation, rec_class = get_recommendation(pds)
                    
                    # Display final decision box immediately below the item description
                    st.markdown(f"""
                    <div class="decision-box">
                        <h2>Final Recommendation</h2>
                        <div class="score">PDS: {pds:+d}</div>
                        <div class="recommendation {rec_class}">{recommendation}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display additional details
                    render_inferred_data(inferences)
                    
                    for factor in ["D", "O", "G", "L", "B"]:
                        explanation = factors.get(f"{factor}_explanation", "No explanation provided.")
                        render_factor_card(factor, int(factors.get(factor, 0)), explanation)
                    
                    st.plotly_chart(create_pds_gauge(pds), use_container_width=True)
                    st.plotly_chart(create_radar_chart(factors), use_container_width=True)
            else:
                st.error("Please provide a valid item name and a cost greater than 0.")
    
    # ---------------------------------------------------------
    # How It Works
    # ---------------------------------------------------------
    elif choice == "How It Works":
        st.header("How It Works")
        st.markdown("""
        <div class="how-it-works-container">
            <h2>Our Process Explained</h2>
            <p>
                <strong>Munger AI</strong> simplifies your purchase decisions through a three-step process:
            </p>
            <ul>
                <li>
                    <strong>Input Your Data:</strong> Enter the name and cost of the item.
                </li>
                <li>
                    <strong>AI Inference:</strong> Our advanced AI analyzes your input to infer key financial details,
                    such as your leftover income, debt status, financial goals, and purchase urgency.
                </li>
                <li>
                    <strong>Factor Evaluation & Scoring:</strong> The AI evaluates five critical factors
                    (Discretionary Income, Opportunity Cost, Goal Alignment, Long-Term Impact, Behavioral)
                    and computes a Purchase Decision Score (PDS). A higher score indicates a more financially sound decision.
                </li>
            </ul>
            <p>
                Visual charts and detailed factor breakdowns help you understand the reasoning behind the final recommendation.
                This ensures you make informed decisions that align with your financial goals.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
if __name__ == "__main__":
    main()
