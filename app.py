import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import plotly.graph_objects as go

# Import your modules
from modules.kg_gnn import kg_gnn_module
from modules.resistance_engine import resistance_engine
from modules.host_protein_model import host_protein_model
from modules.vr_visualization import vr_view
from modules.explainable_ai import explainability_panel
from modules.ai_assistant import ai_explain
from modules.scenario_comparator import scenario_comparator

# ───────────────────────────────────────────────
# Page Configuration
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="V-HIVRAP – Virtual HIV Research & Analysis Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/v-hivrap/issues",
        "Report a bug": "https://github.com/your-repo/v-hivrap/issues",
        "About": "Research simulation tool for HIV drug resistance & host interactions."
    }
)

# ───────────────────────────────────────────────
# ✅ MOBILE-SAFE SIDEBAR COLOR FIX (DO NOT REMOVE)
# ───────────────────────────────────────────────
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #121212 !important;
    }

    section[data-testid="stSidebar"] .nav {
        background-color: #121212 !important;
    }

    section[data-testid="stSidebar"] .nav-link {
        color: #E0E0E0 !important;
        background-color: transparent !important;
        border-radius: 6px;
        margin: 0.2rem 0;
    }

    section[data-testid="stSidebar"] .nav-link:hover {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] .nav-link.active {
        background-color: #2E7D32 !important;
        color: #FFFFFF !important;
        font-weight: 600;
    }

    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            background-color: #121212 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #E0E0E0 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ───────────────────────────────────────────────
# Session State
# ───────────────────────────────────────────────
if "simulations" not in st.session_state:
    st.session_state.simulations = []

if "current_scenario_name" not in st.session_state:
    st.session_state.current_scenario_name = ""

if "app_version" not in st.session_state:
    st.session_state.app_version = "0.1.0"

# ───────────────────────────────────────────────
# Sidebar Navigation
# ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### V-HIVRAP")
    st.caption(f"Version {st.session_state.app_version}")

    selected = option_menu(
        menu_title=None,
        options=[
            "🏠 Home",
            "🧬 Resistance Engine",
            "🧠 Host-Protein Suppression",
            "🤖 Knowledge Graph + GNN",
            "🎮 VR / Advanced Viz",
            "💡 AI Assistant",
            "📊 Scenario Comparator"
        ],
        icons=[
            "house",
            "activity",
            "shield-check",
            "diagram-3",
            "vr",
            "robot",
            "bar-chart-line"
        ],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0.5rem"},
            "nav-link": {
                "font-size": "1.05rem",
                "text-align": "left",
                "margin": "0.2rem",
            },
            "nav-link-selected": {
                "background-color": "#2E7D32"
            },
        }
    )

# ───────────────────────────────────────────────
# Real HIV Drugs
# ───────────────────────────────────────────────
REAL_DRUGS = ["Tenofovir", "Lamivudine", "Dolutegravir", "Efavirenz"]

# ───────────────────────────────────────────────
# Home Page
# ───────────────────────────────────────────────
if selected == "🏠 Home":
    st.title("V-HIVRAP – Virtual HIV Research & Analysis Platform")
    st.markdown(
        "**Research simulation environment for HIV drug resistance, host interactions, and gene editing interventions**"
    )

    with st.expander("About HIV"):
        st.markdown("""
        HIV attacks the immune system and can progress to AIDS without treatment.
        Key challenges include rapid mutation, drug resistance, and complex host-virus interactions.
        """)

    with st.expander("About V-HIVRAP", expanded=True):
        st.markdown("""
        V-HIVRAP is an interactive research platform designed to:
        - Simulate HIV drug resistance
        - Model host protein suppression and gene editing
        - Explore drug–target–mutation graphs
        - Compare multiple treatment scenarios
        - Provide explainable AI insights
        """)

    with st.expander("📖 How to Use V-HIVRAP", expanded=True):
        st.markdown("""
        1. Select a module from the sidebar  
        2. Adjust parameters and run simulations  
        3. All runs are captured automatically  
        4. Compare results in Scenario Comparator  
        5. Use AI Assistant for explanations
        """)

    st.subheader("Quick Viral Load Demo")
    col_l, col_r = st.columns([1, 2])

    with col_l:
        drug_pressure = st.slider("Drug Pressure", 0.0, 1.0, 0.6, 0.05)
        enable_gene = st.checkbox("Enable Gene Editing")
        gene_effect = (
            st.slider("Gene Editing Effectiveness", 0.0, 1.0, 0.5, 0.05)
            if enable_gene else 0.0
        )

    with col_r:
        t = np.linspace(0, 120, 200)
        viral_load = np.exp(-0.05 * t) * (1 + 1.5 * (1 - drug_pressure)) * (1 + 0.8 * (1 - gene_effect))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=viral_load, mode="lines", name="Viral Load"))
        fig.update_layout(
            title="Simulated Viral Load",
            xaxis_title="Time (days)",
            yaxis_title="Relative Viral Load",
            template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Drugs Available in Simulations")
    st.write(", ".join([f"**{d}**" for d in REAL_DRUGS]))

# ───────────────────────────────────────────────
# Other Modules
# ───────────────────────────────────────────────
elif selected == "🧬 Resistance Engine":
    resistance_engine()
    with st.expander("Explainable Insights"):
        explainability_panel()

elif selected == "🧠 Host-Protein Suppression":
    host_protein_model()
    with st.expander("Explainable Insights"):
        explainability_panel()

elif selected == "🤖 Knowledge Graph + GNN":
    kg_gnn_module()

elif selected == "🎮 VR / Advanced Viz":
    vr_view()

elif selected == "💡 AI Assistant":
    ai_explain()

elif selected == "📊 Scenario Comparator":
    scenario_comparator()

# ───────────────────────────────────────────────
# Footer
# ───────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; color:#78909c; font-size:0.9rem; padding:1rem;'>
        V-HIVRAP v0.1.0 • Research simulation tool •
        Developed by Simon •
        Contact: <a href='mailto:symoprof83@gmail.com'>symoprof83@gmail.com</a>
    </div>
    """,
    unsafe_allow_html=True
)
