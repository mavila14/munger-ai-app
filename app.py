import streamlit as st
import re
import json
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------------------------
# Configure your Google Generative AI API key once at the start:
# --------------------------------------------------------------------
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
genai.configure(api_key=GOOGLE_API_KEY)

# We'll reference this model for all calls:
GEMINI_MODEL = "gemini-2.0-flash"

# --------------------------------------------------------------------
# Custom CSS remains unchanged
# --------------------------------------------------------------------
custom_css = """
<style>
/* Typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Base styles */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1a202c;
    -webkit-font-smoothing: antialiased;
}

/* Overall page styling with subtle gradient */
.main {
    background: linear-gradient(145deg, #f8fafc 0%, #edf2f7 100%);
}

/* Header and text styling */
h1 {
    font-weight: 800;
    font-size: 2.5rem;
    letter-spacing: -0.025em;
    color: #1a202c;
    line-height: 1.2;
    margin-bottom: 1rem;
}

h2 {
    font-weight: 700;
    font-size: 1.8rem;
    letter-spacing: -0.025em;
    color: #2d3748;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

h3 {
    font-weight: 600;
    font-size: 1.3rem;
    color: #4a5568;
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
}

p {
    font-size: 1rem;
    line-height: 1.6;
    color: #4a5568;
    margin-bottom: 1rem;
}

/* Layout Containers */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #fff;
    border-right: 1px solid #e2e8f0;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding-top: 2rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

[data-testid="stSidebar"] h1 {
    font-size: 1.5rem;
    color: #5a67d8;
    margin-bottom: 2rem;
}

/* Custom form inputs */
[data-testid="stTextInput"] input, 
[data-testid="stNumberInput"] input, 
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] {
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    padding: 0.75rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    width: 100%;
    margin-bottom: 1rem;
}

[data-testid="stTextInput"] input:focus, 
[data-testid="stNumberInput"] input:focus, 
[data-testid="stTextArea"] textarea:focus {
    border-color: #5a67d8;
    box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.15);
}

/* Buttons */
[data-testid="baseButton-secondary"], 
.stButton button {
    background: linear-gradient(135deg, #5a67d8 0%, #4c51bf 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.025em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 6px rgba(90, 103, 216, 0.2), 0 1px 3px rgba(90, 103, 216, 0.1);
}

[data-testid="baseButton-secondary"]:hover, 
.stButton button:hover {
    background: linear-gradient(135deg, #4c51bf 0%, #434190 100%);
    transform: translateY(-2px);
    box-shadow: 0 7px 14px rgba(90, 103, 216, 0.25), 0 3px 6px rgba(90, 103, 216, 0.15);
}

[data-testid="baseButton-secondary"]:active, 
.stButton button:active {
    transform: translateY(0);
    box-shadow: 0 3px 6px rgba(90, 103, 216, 0.15), 0 1px 3px rgba(90, 103, 216, 0.1);
}

/* Card styling */
.card {
    background-color: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 10px 15px rgba(0, 0, 0, 0.025);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid #f0f4f8;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.07), 0 20px 30px rgba(0, 0, 0, 0.035);
}

/* Decision result box */
.decision-box {
    background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
    border-radius: 12px;
    padding: 2rem 1.5rem;
    margin-top: 2rem;
    border: 1px solid #f0f4f8;
    box-shadow: 0 10px 25px rgba(90, 103, 216, 0.12), 0 4px 10px rgba(90, 103, 216, 0.08);
    text-align: center;
    animation: fadeInUp 0.5s ease-out forwards;
    transform: translateY(20px);
    opacity: 0;
}

.decision-box h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #5a67d8;
    margin-bottom: 1.5rem;
}

.decision-box strong {
    color: #1a202c;
    font-weight: 700;
}

.decision-box .score {
    font-size: 3rem;
    font-weight: 800;
    color: #5a67d8;
    margin: 1rem 0;
    text-shadow: 0 2px 4px rgba(90, 103, 216, 0.2);
}

/* Factor cards */
.factor-card {
    display: flex;
    align-items: center;
    background-color: white;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
    border-left: 4px solid #5a67d8;
}

.factor-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    transform: translateX(3px);
}

.factor-card .factor-letter {
    font-size: 1.25rem;
    font-weight: 700;
    color: #5a67d8;
    margin-right: 1rem;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #ebf4ff;
    border-radius: 50%;
}

.factor-card .factor-description {
    flex: 1;
}

.factor-card .factor-value {
    font-size: 1.25rem;
    font-weight: 700;
    margin-left: auto;
}

.factor-card .factor-value.positive {
    color: #48bb78;
}

.factor-card .factor-value.negative {
    color: #f56565;
}

.factor-card .factor-value.neutral {
    color: #a0aec0;
}

/* Landing page title styling */
.landing-title {
    font-size: 3.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #5a67d8 0%, #4c51bf 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    letter-spacing: -0.05em;
    line-height: 1;
    text-align: center;
}

.landing-subtitle {
    font-size: 1.25rem;
    font-weight: 500;
    color: #4a5568;
    margin-bottom: 2rem;
    text-align: center;
}

/* Logo styling */
.logo {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
}

.logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #5a67d8 0%, #4c51bf 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    color: white;
    font-weight: 700;
    font-size: 1.25rem;
}

.logo-text {
    font-size: 1.5rem;
    font-weight: 800;
    color: #5a67d8;
}

/* Animation keyframes */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(90, 103, 216, 0.4);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(90, 103, 216, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(90, 103, 216, 0);
    }
}

/* Decision recommendation styling */
.recommendation {
    margin-top: 1rem;
    font-size: 1.25rem;
    font-weight: 600;
}

.recommendation.positive {
    color: #48bb78;
}

.recommendation.negative {
    color: #f56565;
}

.recommendation.neutral {
    color: #ed8936;
}

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
}

.section-header h2 {
    margin: 0;
}

.section-icon {
    width: 32px;
    height: 32px;
    background: #ebf4ff;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    color: #5a67d8;
    font-weight: 700;
    font-size: 1rem;
}

/* Item card styles */
.item-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
}

.item-icon {
    width: 40px;
    height: 40px;
    background: #ebf4ff;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 1rem;
    color: #5a67d8;
    font-weight: 700;
    font-size: 1.25rem;
}

.item-details {
    flex: 1;
}

.item-name {
    font-weight: 600;
    font-size: 1.1rem;
    color: #2d3748;
}

.item-cost {
    font-weight: 700;
    font-size: 1.2rem;
    color: #5a67d8;
}

/* Inferred data styles */
.inferred-data {
    background-color: #f8fafc;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    border: 1px dashed #cbd5e0;
}

.inferred-item {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
}

.inferred-label {
    font-weight: 600;
    min-width: 180px;
    color: #4a5568;
}

.inferred-value {
    color: #2d3748;
}

/* Success & Error messages */
.success-message, .error-message {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    animation: fadeInUp 0.3s ease-out forwards;
}

.success-message {
    background-color: #f0fff4;
    border: 1px solid #c6f6d5;
    color: #2f855a;
}

.error-message {
    background-color: #fff5f5;
    border: 1px solid #fed7d7;
    color: #c53030;
}

/* Thinking animation */
.thinking {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 1rem 0;
}

.thinking-dot {
    background-color: #5a67d8;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin: 0 5px;
    animation: thinkingAnimation 1.4s infinite ease-in-out both;
}

.thinking-dot:nth-child(1) {
    animation-delay: -0.32s;
}

.thinking-dot:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes thinkingAnimation {
    0%, 80%, 100% {
        transform: scale(0);
    }
    40% {
        transform: scale(1);
    }
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --------------------------------------------------------------------
# Helper functions for visual elements
# --------------------------------------------------------------------
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

def render_factor_card(factor, value, description):
    # Determine class based on value
    if value > 0:
        value_class = "positive"
    elif value < 0:
        value_class = "negative"
    else:
        value_class = "neutral"
        
    st.markdown(f"""
    <div class="factor-card">
        <div class="factor-letter">{factor}</div>
        <div class="factor-description">{description}</div>
        <div class="factor-value {value_class}">{value:+d}</div>
    </div>
    """, unsafe_allow_html=True)

def render_item_card(item_name, item_cost):
    icon = "💼" if item_cost >= 1000 else "🛍️"
    st.markdown(f"""
    <div class="item-card">
        <div class="item-icon">{icon}</div>
        <div class="item-details">
            <div class="item-name">{item_name}</div>
        </div>
        <div class="item-cost">${item_cost:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

def render_inferred_data(inferred_data):
    st.markdown("""
    <div class="inferred-data">
        <h4>AI-Inferred Data</h4>
    """, unsafe_allow_html=True)
    
    for key, value in inferred_data.items():
        st.markdown(f"""
        <div class="inferred-item">
            <div class="inferred-label">{key}:</div>
            <div class="inferred-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_radar_chart(factors):
    categories = [
        'Discretionary Income', 
        'Opportunity Cost', 
        'Goal Alignment', 
        'Long-Term Impact', 
        'Behavioral'
    ]
    
    values = [
        factors['D'], 
        factors['O'], 
        factors['G'], 
        factors['L'], 
        factors['B']
    ]
    # Add the first value at the end to close the shape
    values.append(values[0])
    categories.append(categories[0])
    
    fig = go.Figure()
    
    # Add radar chart trace
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(90, 103, 216, 0.2)',
        line=dict(color='#5a67d8', width=2),
        name='Factors'
    ))
    
    # Add horizontal lines for reference
    for i in [-2, -1, 0, 1, 2]:
        fig.add_trace(go.Scatterpolar(
            r=[i] * len(categories),
            theta=categories,
            line=dict(color='rgba(200, 200, 200, 0.5)', width=1, dash='dash'),
            name=f'Level {i}',
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-3, 3],
                tickvals=[-2, -1, 0, 1, 2],
                showticklabels=True,
                ticks='',
                linewidth=0,
                gridwidth=0.5,
                gridcolor='rgba(200, 200, 200, 0.3)'
            ),
            angularaxis=dict(
                tickwidth=1,
                linewidth=1,
                gridwidth=1,
                gridcolor='rgba(200, 200, 200, 0.3)'
            ),
            bgcolor='rgba(255, 255, 255, 0.9)'
        ),
        showlegend=False,
        margin=dict(l=70, r=70, t=20, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_pds_gauge(pds):
    # Define gauge colors based on value
    if pds >= 5:
        color = "#48bb78"  # Green for positive
    elif pds < 0:
        color = "#f56565"  # Red for negative
    else:
        color = "#ed8936"  # Orange for neutral
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pds,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [-10, 10], 'tickwidth': 1, 'tickcolor': "#2d3748"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [-10, 0], 'color': '#fed7d7'},
                {'range': [0, 5], 'color': '#feebc8'},
                {'range': [5, 10], 'color': '#c6f6d5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#2d3748", 'family': "Inter, sans-serif"}
    )
    
    return fig

# --------------------------------------------------------------------
# New function: Infer additional details from item name and cost
# --------------------------------------------------------------------
def infer_purchase_details(item_name, item_cost):
    """
    Use Gemini to infer additional purchase details based on the item name and cost.
    Returns a dictionary with inferred values for all required fields.
    """
    prompt_text = f"""
You are a financial advisor AI that needs to infer details about a purchase decision.
Based only on the item name and cost, infer reasonable values for:
1. Monthly leftover income (typical disposable income after expenses for someone who might buy this)
2. Whether the buyer likely has high-interest debt (Yes/No)
3. What the buyer's main financial goal might be
4. How urgent this purchase is (Urgent Needs/Mostly Wants/Mixed)

Item: "{item_name}"
Cost: ${item_cost:.2f}

Provide your response in valid JSON format only:
{{
  "leftover_income": 2000,
  "has_high_interest_debt": "Yes",
  "main_financial_goal": "Save for retirement",
  "purchase_urgency": "Mostly Wants"
}}
    """.strip()

    try:
        # Create the model and generate content
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt_text,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=512
            )
        )

        if not response:
            st.error("No response returned from the Gemini model.")
            return get_default_inferences(item_cost)

        output_text = response.text
        # Attempt to extract JSON from the output
        candidates = re.findall(r"(\{[\s\S]*?\})", output_text)
        for candidate in candidates:
            try:
                data = json.loads(candidate)
                required_keys = ["leftover_income", "has_high_interest_debt", 
                                "main_financial_goal", "purchase_urgency"]
                if all(k in data for k in required_keys):
                    return data
            except json.JSONDecodeError:
                continue

        st.error("Unable to parse valid JSON from model output.")
        return get_default_inferences(item_cost)

    except Exception as e:
        st.error(f"Error calling Gemini model: {e}")
        return get_default_inferences(item_cost)

def get_default_inferences(item_cost):
    """Provide default values when inference fails"""
    # Scale leftover income based on item cost
    leftover_income = max(1000, item_cost * 2)
    
    return {
        "leftover_income": leftover_income,
        "has_high_interest_debt": "No",
        "main_financial_goal": "Save for emergencies",
        "purchase_urgency": "Mixed"
    }

# --------------------------------------------------------------------
# get_factors_from_gemini: Using the updated google-generativeai library
# --------------------------------------------------------------------
def get_factors_from_gemini(
    leftover_income: float,
    has_high_interest_debt: str,
    main_financial_goal: str,
    purchase_urgency: str,
    item_name: str,
    item_cost: float
) -> dict:
    """
    Calls the Gemini 2.0 Flash model with a prompt that explains how to assign each factor.
    Returns factor values (D, O, G, L, B) as integers in the range -2 to +2.
    """
    prompt_text = f"""
We have a Purchase Decision Score (PDS) formula:
PDS = D + O + G + L + B,
where each factor is an integer from -2 to +2.

Guidelines:
1. D (Discretionary Income Factor): Rate higher if leftover_income is much larger than item_cost.
2. O (Opportunity Cost Factor): Rate positive if no high-interest debt and cost is negligible compared to goals; negative if high-interest debt exists.
3. G (Goal Alignment Factor): Rate positive if the purchase strongly supports the main financial goal; negative if it conflicts.
4. L (Long-Term Impact Factor): Rate positive if the purchase has lasting benefits; negative if it creates ongoing costs.
5. B (Behavioral/Psychological Factor): Rate positive if the purchase is urgently needed and reduces stress; negative if it is impulsive.

Evaluate the following scenario:
- Item: "{item_name}"
- Cost: {item_cost} USD
- Monthly Leftover Income: {leftover_income} USD
- High-interest debt: {has_high_interest_debt}
- Main Financial Goal: {main_financial_goal}
- Purchase Urgency: {purchase_urgency}

Also provide a brief, one-sentence explanation for each factor.

Assign integer values from -2 to +2 for each factor (D, O, G, L, B) according to the guidelines.
Return the result in valid JSON format, for example:
{{
  "D": 2,
  "O": 2,
  "G": 2,
  "L": 2,
  "B": 2,
  "D_explanation": "The item cost is less than 10% of monthly leftover income.",
  "O_explanation": "No high-interest debt and the cost is small relative to financial goals.",
  "G_explanation": "This purchase directly supports the main financial goal.",
  "L_explanation": "The item provides long-term benefits with minimal ongoing costs.",
  "B_explanation": "This purchase addresses an urgent need and reduces stress."
}}
    """.strip()

    try:
        # Create the model and generate content
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt_text,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=512
            )
        )

        if not response:
            st.error("No response returned from the Gemini model.")
            return {"D": 0, "O": 0, "G": 0, "L": 0, "B": 0}

        output_text = response.text
        # Attempt to extract JSON from the output
        candidates = re.findall(r"(\{[\s\S]*?\})", output_text)
        for candidate in candidates:
            try:
                data = json.loads(candidate)
                if all(k in data for k in ["D", "O", "G", "L", "B"]):
                    return data
            except json.JSONDecodeError:
                continue

        st.error("Unable to parse valid JSON from model output.")
        return {"D": 0, "O": 0, "G": 0, "L": 0, "B": 0}

    except Exception as e:
        st.error(f"Error calling Gemini model: {e}")
        return {"D": 0, "O": 0, "G": 0, "L": 0, "B": 0}

def compute_pds(factors: dict) -> int:
    """Compute the Purchase Decision Score as a sum of factors."""
    return sum(factors.get(k, 0) for k in ["D", "O", "G", "L", "B"])

def get_recommendation(pds: int) -> tuple:
    """Return a recommendation based on the PDS."""
    if pds >= 5:
        return "Buy it.", "positive"
    elif pds < 0:
        return "Don't buy it.", "negative"
    else:
        return "Consider carefully.", "neutral"

# --------------------------------------------------------------------
# Main application
# --------------------------------------------------------------------
def main():
    # Sidebar
    with st.sidebar:
        render_logo()
        st.markdown("##### Decision Assistant")
        
        pages = ["Decision Tool", "How It Works", "Examples"]
        selection = st.radio("", pages, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### Quick Tips")
        st.markdown("""
        - Just enter the item and cost
        - Our AI will analyze the rest
        - Higher score = better purchase
        - Scores above 5 are recommended
        """)
        
        st.markdown("---")
        st.markdown("© 2025 Munger AI")
    
    # Landing Page Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 class="landing-title">Munger AI</h1>
        <p class="landing-subtitle">Should you buy it? Our AI decides in seconds.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if selection == "Decision Tool":
        # Simplified purchase decision form
        render_section_header("What are you buying?", "🛍️")
        
        with st.form("simplified_purchase_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                item_name = st.text_input("What are you buying?", value="New Laptop")
            with col2:
                item_cost = st.number_input("Cost ($)", min_value=1.0, value=500.0, step=50.0)
            
            submit_button = st.form_submit_button("Should I Buy It?", use_container_width=True)
        
        if submit_button:
            with st.spinner("AI is analyzing your purchase..."):
                # First, infer additional details based on item name and cost
                inferred_details = infer_purchase_details(item_name, item_cost)
                
                # Display the item card
                render_item_card(item_name, item_cost)
                
                # Show inferred data in a nice format
                render_inferred_data({
                    "Monthly leftover income": f"${inferred_details['leftover_income']:,.2f}",
                    "High-interest debt": inferred_details['has_high_interest_debt'],
                    "Main financial goal": inferred_details['main_financial_goal'],
                    "Purchase urgency": inferred_details['purchase_urgency']
                })
                
                # Get decision factors using inferred details
                factors = get_factors_from_gemini(
                    leftover_income=inferred_details['leftover_income'],
                    has_high_interest_debt=inferred_details['has_high_interest_debt'],
                    main_financial_goal=inferred_details['main_financial_goal'],
                    purchase_urgency=inferred_details['purchase_urgency'],
                    item_name=item_name,
                    item_cost=item_cost
                )
                
                # Calculate PDS and get recommendation
                pds = compute_pds(factors)
                recommendation, rec_class = get_recommendation(pds)
                
                # Display results
                st.markdown(f"""
                <div class="decision-box">
                    <h2>Purchase Decision Score</h2>
                    <div class="score">{pds}</div>
                    <div class="recommendation {rec_class}">{recommendation}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Two columns for radar chart and gauge
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Decision Factors")
                    factor_descriptions = {
                        'D': 'Discretionary Income',
                        'O': 'Opportunity Cost', 
                        'G': 'Goal Alignment',
                        'L': 'Long-Term Impact',
                        'B': 'Behavioral'
                    }
                    for factor, description in factor_descriptions.items():
                        render_factor_card(factor, factors[factor], description)
                        if f"{factor}_explanation" in factors:
                            st.caption(factors[f"{factor}_explanation"])
                
                with col2:
                    st.markdown("### Factor Analysis")
                    radar_fig = create_radar_chart(factors)
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    gauge_fig = create_pds_gauge(pds)
                    st.plotly_chart(gauge_fig, use_container_width=True)
                
                # Display insights
                st.markdown("### Decision Insights")
                
                
                # Generate insights based on factors
                insights = []
                
                # Get the direction of the recommendation
                if pds >= 5:
                    insights.append(f"✅ Based on our analysis, buying the {item_name} is a good financial decision.")
                elif pds < 0:
                    insights.append(f"⚠️ Our analysis suggests that buying the {item_name} may not be the best financial decision right now.")
                else:
                    insights.append(f"⚖️ This purchase could be reasonable, but carefully consider if the {item_name} is truly necessary.")
                
                # Add insights based on the strongest factors (positive or negative)
                factor_keys = ["D", "O", "G", "L", "B"]
                for factor in factor_keys:
                    if factors[factor] >= 2:
                        insights.append(f"✅ {factors.get(f'{factor}_explanation', 'Strong positive for this factor.')}")
                    elif factors[factor] <= -2:
                        insights.append(f"⚠️ {factors.get(f'{factor}_explanation', 'Strong negative for this factor.')}")
                
                # Add a recommendation
                if pds >= 5:
                    insights.append("✅ Go ahead with this purchase.")
                elif pds < 0:
                    if factors["D"] < 0:
                        insights.append("⚠️ Consider saving more before making this purchase.")
                    elif factors["O"] < 0:
                        insights.append("⚠️ Focus on paying down high-interest debt first.")
                    elif factors["L"] < 0:
                        insights.append("⚠️ Look for alternatives with better long-term value.")
                    else:
                        insights.append("⚠️ Consider waiting or finding less expensive alternatives.")
                else:
                    insights.append("⚖️ If you decide to proceed, make sure this purchase doesn't impact other financial priorities.")
                
                for insight in insights:
                    st.markdown(f"- {insight}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif selection == "How It Works":
        st.markdown("## How Munger AI Works")
        st.markdown("""
        <div class="card">
            <h3>Simple, AI-Powered Purchase Decisions</h3>
            <p>Munger AI uses advanced artificial intelligence to help you make better buying decisions, inspired by Charlie Munger's mental models.</p>
            
            <h4>1. Just Tell Us What You're Buying</h4>
            <p>Enter only two things:</p>
            <ul>
                <li>What you want to buy</li>
                <li>How much it costs</li>
            </ul>
            
            <h4>2. Our AI Fills in the Rest</h4>
            <p>Based on what you're buying and its cost, our AI intuits:</p>
            <ul>
                <li>Your likely monthly discretionary income</li>
                <li>Whether you might have high-interest debt</li>
                <li>What financial goals you might have</li>
                <li>How urgently you need this purchase</li>
            </ul>
            
            <h4>3. Get Your Purchase Decision Score</h4>
            <p>We calculate your Purchase Decision Score (PDS) using five key factors:</p>
            <ul>
                <li><strong>D</strong>: Discretionary Income Factor</li>
                <li><strong>O</strong>: Opportunity Cost Factor</li>
                <li><strong>G</strong>: Goal Alignment Factor</li>
                <li><strong>L</strong>: Long-Term Impact Factor</li>
                <li><strong>B</strong>: Behavioral/Psychological Factor</li>
            </ul>
            
            <h4>4. Make a Smarter Decision</h4>
            <p>A score of 5 or higher means "Buy it." A negative score means "Don't buy it." Anything in between requires careful consideration.</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif selection == "Examples":
        st.markdown("## Example Purchases")
        
        examples = [
            {
                "title": "Essential Professional Upgrade",
                "item": "High-Performance Laptop",
                "cost": 1200,
                "description": "A powerful laptop for a professional who needs it for work",
                "likely_score": "High (5+)"
            },
            {
                "title": "Luxury Purchase",
                "item": "Designer Watch",
                "cost": 5000,
                "description": "An expensive luxury watch as a status symbol",
                "likely_score": "Low (Negative)"
            },
            {
                "title": "Home Investment",
                "item": "Quality Mattress",
                "cost": 800,
                "description": "A high-quality mattress to improve sleep and health",
                "likely_score": "High (5+)"
            },
            {
                "title": "Impulse Purchase",
                "item": "Latest Smartphone",
                "cost": 1000,
                "description": "Upgrading to the newest smartphone when current one works fine",
                "likely_score": "Medium (0-4)"
            }
        ]
        
        for example in examples:
            st.markdown(f"""
            <div class="card">
                <h3>{example["title"]}</h3>
                <div class="item-card">
                    <div class="item-icon">🛍️</div>
                    <div class="item-details">
                        <div class="item-name">{example["item"]}</div>
                        <div>{example["description"]}</div>
                    </div>
                    <div class="item-cost">${example["cost"]:,.2f}</div>
                </div>
                <p><strong>Likely PDS:</strong> {example["likely_score"]}</p>
                
                <form action="">
                    <button type="submit" class="stButton">Try This Example</button>
                </form>
            </div>
            """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()
