import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.express as px
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(
    page_title="Chi-Square Goodness of Fit",
    page_icon="📊",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- Functions ---

@st.cache_data
def load_data(file):
    """Loads data from CSV or Excel file."""
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def validate_columns(df, cat_col, obs_col, exp_col):
    """Validates that selected columns exist, are numeric where needed, and correspond correctly."""
    if not (cat_col and obs_col and exp_col):
        return False, "Please select all required columns."
    
    if obs_col == exp_col:
         return False, "Observed and Expected columns cannot be the same."

    if not pd.api.types.is_numeric_dtype(df[obs_col]):
        return False, f"Column '{obs_col}' must be numeric."
    
    if not pd.api.types.is_numeric_dtype(df[exp_col]):
        return False, f"Column '{exp_col}' must be numeric."
        
    if df[obs_col].isnull().any() or df[exp_col].isnull().any():
        return False, "Selected columns contain missing values (NaN). Please clean your data."
        
    return True, ""

@st.cache_data
def calculate_metrics(f_obs, f_exp, alpha):
    """Calculates Chi-Square statistics."""
    chi2_score, p_value = stats.chisquare(f_obs=f_obs, f_exp=f_exp)
    deg_of_freedom = len(f_obs) - 1
    critical_value = stats.chi2.ppf(1 - alpha, deg_of_freedom)
    return chi2_score, p_value, critical_value, deg_of_freedom

def plot_observed_vs_expected(df_melted, cat_col):
    """Creates an interactive grouped bar chart using Plotly."""
    fig = px.bar(
        df_melted, 
        x=cat_col, 
        y="Count", 
        color="Type", 
        barmode="group",
        title="Observed vs Expected Counts",
        color_discrete_map={"Observed": "#636EFA", "Expected": "#EF553B"},
        text="Count"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis_title="Count", xaxis_title=cat_col)
    return fig

def plot_chi_square_dist(chi2_score, critical_value, deg_of_freedom, alpha, p_value):
    """Creates an interactive distribution plot with shaded regions."""
    x_max = max(critical_value, chi2_score) + 5
    if x_max < 20: x_max = 20 # Minimum range for visualization
    
    x = np.linspace(0, x_max, 1000)
    y = stats.chi2.pdf(x, deg_of_freedom)
    
    fig = go.Figure()
    
    # 1. Main PDF Line
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f'Chi2 PDF (df={deg_of_freedom})', line=dict(color='black')))
    
    # 2. Critical Region (Shading) - Orange
    x_crit = x[x >= critical_value]
    y_crit = y[x >= critical_value]
    # We add a point at (x=critical_value, y=0) and (x_max, 0) to close the polygon for fill
    x_fill_crit = np.concatenate(([critical_value], x_crit, [x_max]))
    y_fill_crit = np.concatenate(([0], y_crit, [0]))
    
    fig.add_trace(go.Scatter(
        x=x_fill_crit, 
        y=y_fill_crit, 
        fill='toself', 
        fillcolor='rgba(255, 165, 0, 0.3)', 
        line=dict(width=0),
        name=f'Critical Region (α={alpha})',
        hoverinfo='skip'
    ))

    # 3. P-Value Region (Shading) - Blue (if result is significant/visible)
    # Only shade if it's visible on graph
    if chi2_score < x_max:
        x_p = x[x >= chi2_score]
        y_p = y[x >= chi2_score]
        if len(x_p) > 0:
            x_fill_p = np.concatenate(([chi2_score], x_p, [x_max]))
            y_fill_p = np.concatenate(([0], y_p, [0]))
            
            fig.add_trace(go.Scatter(
                x=x_fill_p, 
                y=y_fill_p, 
                fill='toself', 
                fillcolor='rgba(0, 0, 255, 0.2)', 
                line=dict(width=0),
                name=f'P-Value Region (p={p_value:.4f})',
                hoverinfo='skip'
            ))

    # 4. Vertical Lines
    fig.add_vline(x=critical_value, line_width=2, line_dash="dash", line_color="orange", annotation_text=f" Crit: {critical_value:.2f}", annotation_position="top right")
    fig.add_vline(x=chi2_score, line_width=2, line_color="blue", annotation_text=f" Stat: {chi2_score:.2f}", annotation_position="top right")

    # Layout updates
    fig.update_layout(
        title="Chi-Square Distribution Visualization",
        xaxis_title="Chi-Square Statistic",
        yaxis_title="Probability Density",
        template="plotly_white",
        height=500
    )
    return fig

# --- App Layout ---

st.markdown('<div class="main-header">📊 Chi-Square Goodness of Fit Test</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    data_source = st.radio("Data Source", ["Upload File", "Manual Entry"])
    
    df = None
    if data_source == "Upload File":
        uploaded_file = st.file_uploader("Upload Data (CSV or Excel)", type=["csv", "xlsx"])
        if uploaded_file:
            df = load_data(uploaded_file)
    else:
        st.info("Enter data directly into the table below.")
        # Default manual data
        manual_data = {
            "Category": ["A", "B", "C"],
            "Observed": [10, 20, 30],
            "Expected": [20, 20, 20]
        }
        edited_df = st.data_editor(pd.DataFrame(manual_data), num_rows="dynamic", use_container_width=True)
        if not edited_df.empty:
            df = edited_df

    alpha = st.slider("Significance Level (Alpha)", 0.01, 0.10, 0.05, 0.01)


# Main Content
if df is not None:
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(), use_container_width=True)
    
    st.subheader("🛠️ Column Selection")
    cols = df.columns.tolist()
    
    c1, c2, c3 = st.columns(3)
    cat_col = c1.selectbox("Category Column", cols, index=0 if len(cols)>0 else None)
    obs_col = c2.selectbox("Observed Column", cols, index=1 if len(cols)>1 else None)
    exp_col = c3.selectbox("Expected Column", cols, index=2 if len(cols)>2 else None)
    
    st.markdown("### Hypothesis")
    st.info("""
    **Null Hypothesis ($H_0$):** There is **no significant difference** between the observed and expected values.
    
    **Alternative Hypothesis ($H_1$):** There **is a significant difference** between the observed and expected values.
    """)
    
    if st.button("🚀 Run Test", type="primary"):
        # Validation
        is_valid, msg = validate_columns(df, cat_col, obs_col, exp_col)
        
        if is_valid:
            f_obs = df[obs_col]
            f_exp = df[exp_col]
            
            # Metrics
            chi2_score, p_value, critical_value, dof = calculate_metrics(f_obs, f_exp, alpha)
            
            st.divider()
            st.header("Results")
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Chi-Square Score", f"{chi2_score:.4f}")
            m2.metric("P-Value", f"{p_value:.4f}")
            m3.metric("Critical Value", f"{critical_value:.4f}")
            m4.metric("Deg. of Freedom", f"{dof}")
            
            # Conclusion Alert
            if p_value < alpha:
                st.error(f"**Reject H0**: The difference is statistically significant (p < {alpha}).")
            else:
                st.success(f"**Fail to Reject H0**: The difference is NOT statistically significant (p >= {alpha}).")
            
            st.divider()
            
            # Visualizations uses Tabs
            tab1, tab2 = st.tabs(["📊 Observed vs Expected", "bell Chi-Square Distribution"])
            
            with tab1:
                df_melted = df.melt(id_vars=cat_col, value_vars=[obs_col, exp_col], var_name="Type", value_name="Count")
                fig_bar = plot_observed_vs_expected(df_melted, cat_col)
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with tab2:
                fig_dist = plot_chi_square_dist(chi2_score, critical_value, dof, alpha, p_value)
                st.plotly_chart(fig_dist, use_container_width=True)
                
        else:
            st.error(f"Validation Error: {msg}")

else:
    st.info("👈 Please upload a file or define data manually to proceed.")
