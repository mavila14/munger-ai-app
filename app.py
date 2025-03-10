import streamlit as st
import re
import json
import google.generativeai as genai
import plotly.graph_objects as go

# ------------------------------------------------------------
# Configure your Google Generative AI API key
# ------------------------------------------------------------
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
genai.configure(api_key=GOOGLE_API_KEY)

GEMINI_MODEL = "gemini-2.0-flash"

# ------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1a202c;
    -webkit-font-smoothing: antialiased;
}

.main {
    background: linear-gradient(145deg, #f8fafc 0%, #edf2f7 100%);
}

/* Headings */
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

/* Eye-catching button styling */
[data-testid="baseButton-secondary"], 
.stButton button {
    background: linear-gradient(135deg, #C084FC 0%, #A855F7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.025em !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 6px rgba(168,85,247, 0.3), 0 1px 3px rgba(168,85,247, 0.2) !important;
}
[data-testid="baseButton-secondary"]:hover, 
.stButton button:hover {
    background: linear-gradient(135deg, #9F7AEA 0%, #7B2CBF 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 14px rgba(122, 64, 228, 0.3), 0 3px 6px rgba(122, 64, 228, 0.2) !important;
}
[data-testid="baseButton-secondary"]:active, 
.stButton button:active {
    transform: translateY(0) !important;
    box-shadow: 0 3px 6px rgba(122, 64, 228, 0.2), 0 1px 3px rgba(122, 64, 228, 0.1) !important;
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

/* Section header */
.section-header {
    display: flex;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
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

/* Decision box */
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
.decision-box .score {
    font-size: 3rem;
    font-weight: 800;
    color: #5a67d8;
    margin: 1rem 0;
    text-shadow: 0 2px 4px rgba(90, 103, 216, 0.2);
}
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

/* Animations */
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
# Plotly Charts
# ------------------------------------------------------------
def create_radar_chart(factors):
    categories = ["Discretionary Income","Opportunity Cost","Goal Alignment","Long-Term Impact","Behavioral"]
    vals = [factors["D"], factors["O"], factors["G"], factors["L"], factors["B"]]
    vals.append(vals[0])  # close shape
    categories.append(categories[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=categories,
        fill='toself',
        fillcolor='rgba(90, 103, 216, 0.2)',
        line=dict(color='#5a67d8', width=2),
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
                visible=True, range=[-3,3],
                tickvals=[-2,-1,0,1,2],
                gridcolor='rgba(200,200,200,0.3)'
            ),
            angularaxis=dict(gridcolor='rgba(200,200,200,0.3)'),
            bgcolor='rgba(255,255,255,0.9)'
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=20, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_pds_gauge(pds):
    if pds >= 5:
        color = "#48bb78"
    elif pds < 0:
        color = "#f56565"
    else:
        color = "#ed8936"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pds,
        domain={'x':[0,1],'y':[0,1]},
        gauge={
            'axis': {'range':[-10,10]},
            'bar': {'color':color},
            'bgcolor':"white",
            'borderwidth':2,
            'bordercolor':"#e2e8f0",
            'steps': [
                {'range':[-10,0], 'color':'#fed7d7'},
                {'range':[0,5], 'color':'#feebc8'},
                {'range':[5,10], 'color':'#c6f6d5'}
            ],
        }
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color':"#2d3748", 'family':"Inter, sans-serif"}
    )
    return fig

# ------------------------------------------------------------
# AI Logic
# ------------------------------------------------------------
def get_factors_from_gemini(leftover_income, has_high_interest_debt,
                            main_financial_goal, purchase_urgency,
                            item_name, item_cost, extra_context=None):
    """
    Returns factor assignments (D,O,G,L,B) from -2..+2 plus brief explanations.
    """
    import google.generativeai as genai
    extra_text = f"\nAdditional user context: {extra_context}" if extra_context else ""
    
    prompt = f"""
We have a Purchase Decision Score (PDS) formula:
PDS = D + O + G + L + B, each factor is -2 to 2.

Guidelines:
1. D: Higher if leftover_income >> item_cost
2. O: Positive if no high-interest debt, negative if debt
3. G: Positive if aligns with main_financial_goal, negative if conflicts
4. L: Positive if long-term benefit, negative if extra cost
5. B: Positive if urgent need, negative if impulsive want

Evaluate:
- Item: {item_name}
- Cost: {item_cost}
- leftover_income: {leftover_income}
- high_interest_debt: {has_high_interest_debt}
- main_financial_goal: {main_financial_goal}
- purchase_urgency: {purchase_urgency}
{extra_text}

Return valid JSON:
{{
  "D": 2,
  "O": 1,
  "G": 0,
  "L": -1,
  "B": 2,
  "D_explanation": "...",
  ...
}}
    """.strip()
    
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
        candidates = re.findall(r"(\{[\s\S]*?\})", text)
        for c in candidates:
            try:
                data = json.loads(c)
                if all(k in data for k in ["D","O","G","L","B"]):
                    return data
            except json.JSONDecodeError:
                pass
        st.error("Unable to parse valid JSON from AI output.")
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
# Additional UI Helpers
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

def render_factor_card(factor, value, description):
    if value > 0:
        val_class = "positive"
    elif value < 0:
        val_class = "negative"
    else:
        val_class = "neutral"
    st.markdown(f"""
    <div class="factor-card">
        <div class="factor-letter">{factor}</div>
        <div class="factor-description">{description}</div>
        <div class="factor-value {val_class}">{value:+d}</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Main App
# ------------------------------------------------------------
def main():
    with st.sidebar:
        render_logo()
        st.markdown("##### Decision Assistant")
        
        # Only two pages now:
        pages = ["Decision Tool", "Advanced Tool"]
        selection = st.radio("", pages, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### Quick Tips")
        st.markdown("""
        - Just enter the item and cost
        - Or use Advanced Tool for more control
        - Score above 5 = buy
        """)
        
        st.markdown("---")
        st.markdown("© 2025 Munger AI")
    
    # Main heading (always shown)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 class="landing-title">Munger AI</h1>
        <p class="landing-subtitle">Should you buy it? Our AI decides in seconds.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # -----------------------------------
    # 1. Basic Decision Tool
    # -----------------------------------
    if selection == "Decision Tool":
        render_section_header("What are you buying?", "🛍️")
        # Basic form
        with st.form("basic_form"):
            col1, col2 = st.columns([3,1])
            with col1:
                item_name = st.text_input("What are you buying?", value="New Laptop")
            with col2:
                cost = st.number_input("Cost ($)", min_value=1.0, value=500.0, step=50.0)
            
            submit_btn = st.form_submit_button("Should I Buy It?")
        
        if submit_btn:
            with st.spinner("Analyzing with AI..."):
                # Minimal logic for leftover etc. (could be expanded)
                leftover_income = max(1000, cost * 2)
                has_high_interest_debt = "No"
                main_financial_goal = "Save for emergencies"
                purchase_urgency = "Mixed"
                
                factors = get_factors_from_gemini(
                    leftover_income,
                    has_high_interest_debt,
                    main_financial_goal,
                    purchase_urgency,
                    item_name,
                    cost
                )
                pds = compute_pds(factors)
                rec_text, rec_class = get_recommendation(pds)
                
                render_item_card(item_name, cost)
                st.markdown(f"""
                <div class="decision-box">
                    <h2>Purchase Decision Score</h2>
                    <div class="score">{pds}</div>
                    <div class="recommendation {rec_class}">{rec_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Decision Factors")
                    factor_labels = {
                        "D": "Discretionary Income",
                        "O": "Opportunity Cost",
                        "G": "Goal Alignment",
                        "L": "Long-Term Impact",
                        "B": "Behavioral"
                    }
                    for f in ["D","O","G","L","B"]:
                        render_factor_card(f, factors[f], factor_labels[f])
                        if f"{f}_explanation" in factors:
                            st.caption(factors[f"{f}_explanation"])
                with c2:
                    st.markdown("### Factor Analysis")
                    radar_fig = create_radar_chart(factors)
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    gauge_fig = create_pds_gauge(pds)
                    st.plotly_chart(gauge_fig, use_container_width=True)
    
    # -----------------------------------
    # 2. Advanced Tool
    # -----------------------------------
    else:  # selection == "Advanced Tool"
        render_section_header("Advanced Purchase Query", "⚙️")
        st.markdown("""
        Customize **all** parameters for a more precise analysis.
        """)
        
        with st.form("advanced_form"):
            st.subheader("Purchase Details")
            item_name = st.text_input("Item Name", "High-End Laptop")
            item_cost = st.number_input("Item Cost ($)", min_value=1.0, value=2000.0, step=100.0)
            
            st.subheader("User-Financial Data")
            leftover_income = st.number_input("Monthly Leftover Income ($)", min_value=0.0, value=1500.0, step=100.0)
            has_debt = st.selectbox("High-Interest Debt?", ["No", "Yes"])
            main_goal = st.text_input("Main Financial Goal", "Build an emergency fund")
            urgency = st.selectbox("Purchase Urgency", ["Urgent Needs","Mixed","Mostly Wants"])
            
            st.subheader("Optional Extra Context")
            extra_notes = st.text_area("Any additional context or notes?")
            
            advanced_submit = st.form_submit_button("Analyze My Purchase")
        
        if advanced_submit:
            with st.spinner("Contacting AI for advanced analysis..."):
                factors = get_factors_from_gemini(
                    leftover_income,
                    has_debt,
                    main_goal,
                    urgency,
                    item_name,
                    item_cost,
                    extra_context=extra_notes
                )
                pds = compute_pds(factors)
                rec_text, rec_class = get_recommendation(pds)
                
                render_item_card(item_name, item_cost)
                st.markdown(f"""
                <div class="decision-box">
                    <h2>Purchase Decision Score</h2>
                    <div class="score">{pds}</div>
                    <div class="recommendation {rec_class}">{rec_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Decision Factors")
                    factor_labels = {
                        "D": "Discretionary Income",
                        "O": "Opportunity Cost",
                        "G": "Goal Alignment",
                        "L": "Long-Term Impact",
                        "B": "Behavioral"
                    }
                    for f in ["D","O","G","L","B"]:
                        render_factor_card(f, factors[f], factor_labels[f])
                        if f"{f}_explanation" in factors:
                            st.caption(factors[f"{f}_explanation"])
                with c2:
                    st.markdown("### Factor Analysis")
                    radar_fig = create_radar_chart(factors)
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    gauge_fig = create_pds_gauge(pds)
                    st.plotly_chart(gauge_fig, use_container_width=True)

# ------------------------------------------------------------
# Run the App
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
