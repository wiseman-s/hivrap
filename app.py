import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import plotly.graph_objects as go

# Import your modules (assuming they are in a 'modules' folder)
from modules.kg_gnn import kg_gnn_module
from modules.resistance_engine import resistance_engine
from modules.host_protein_model import host_protein_model
from modules.vr_visualization import vr_view
from modules.explainable_ai import explainability_panel
from modules.ai_assistant import ai_explain
from modules.scenario_comparator import scenario_comparator

# ───────────────────────────────────────────────
# Page Configuration (modern & accessible-friendly)
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="V-HIVRAP – Virtual HIV Research & Analysis Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/v-hivrap/issues',
        'Report a bug': 'https://github.com/your-repo/v-hivrap/issues',
        'About': "V-HIVRAP v0.1 MVP – Research simulation tool for HIV drug resistance & host interactions."
    }
)

# ───────────────────────────────────────────────
# Initialize Session State
# ───────────────────────────────────────────────
if "simulations" not in st.session_state:
    st.session_state.simulations = []           # list of dicts: each saved run {id, name, type, data, params, timestamp}

if "current_scenario_name" not in st.session_state:
    st.session_state.current_scenario_name = ""

if "app_version" not in st.session_state:
    st.session_state.app_version = "0.1.0 MVP"

# ───────────────────────────────────────────────
# Sidebar Navigation
# ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### V-HIVRAP")
    st.caption(f"Version {st.session_state.app_version}")

    selected = option_menu(
        menu_title=None,  # No title to save space
        options=[
            "🏠 Home",
            "🧬 Resistance Engine",
            "🧠 Host-Protein Suppression",
            "🤖 Knowledge Graph + GNN",
            "🎮 VR / Advanced Viz",
            "💡 AI Assistant",
            "📊 Scenario Comparator"
        ],
        icons=["house", "activity", "shield-check", "diagram-3", "vr", "robot", "bar-chart-line"],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0.5rem", "background-color": "#f0f2f6"},
            "nav-link": {"font-size": "1.1rem", "text-align": "left", "margin": "0.2rem", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#2e7d32"},
        }
    )

# ───────────────────────────────────────────────
# Real HIV Drugs List
# ───────────────────────────────────────────────
REAL_DRUGS = ["Tenofovir", "Lamivudine", "Dolutegravir", "Efavirenz"]

# ───────────────────────────────────────────────
# Home Page
# ───────────────────────────────────────────────
if selected == "🏠 Home":
    st.title("V-HIVRAP – Virtual HIV Research & Analysis Platform")
    st.markdown("**Research simulation environment for HIV drug resistance, host interactions, and gene editing interventions**")

    # ── About HIV ────────────────────────────────────────
    with st.expander("About HIV", expanded=False):
        st.markdown("""
        Human Immunodeficiency Virus (**HIV**) targets the immune system. Without treatment, it can progress to AIDS.  
        Key challenges include **drug resistance**, rapid viral mutation, and complex host-virus dynamics.
        """)

    # ── About Platform ───────────────────────────────────
    with st.expander("About V-HIVRAP", expanded=True):
        st.markdown("""
        V-HIVRAP is an **interactive virtual platform** for researchers to:
        - Simulate **drug resistance evolution**
        - Model **host-mediated suppression** & gene editing
        - Explore **drug-target-mutation graphs** with GNN insights
        - Visualize viral populations in 3D
        - Compare scenarios & get explainable AI support
        """)

    # ── How to Use – now expandable ────────────────────────────────
    with st.expander("📖 How to Use V-HIVRAP", expanded=True):
        st.markdown("""
        This platform is designed for quick, iterative exploration of HIV treatment scenarios.  
        **No manual saving required** — everything flows automatically.

        1. **Start here on Home**  
           Play with the quick viral load demo below to get a feeling for the system.

        2. **Choose a module from the sidebar**  
           - Adjust parameters (drugs, sliders, checkboxes, etc.)  
           - Click **Run Simulation** (or equivalent button)

        3. **Results are captured automatically**  
           Every run is added to your current session.

        4. **Compare & analyze**  
           Switch to **Scenario Comparator** tab → see all your runs side-by-side  
           Export curves / parameters as CSV/JSON whenever needed

        5. **Get explanations**  
           Use the **AI Assistant** tab for plain-language explanations  
           Open **Explainable Insights** expanders in modules for key factors

        6. **Visualize deeper**  
           Explore pathways in **Knowledge Graph + GNN**  
           Observe viral particles in **VR / Advanced Viz**

        **Quick tips**  
        • All data stays in your browser session (close tab → reset)  
        • Run dozens of scenarios — Comparator collects them all  
        • Use consistent real drug names across modules  
        • Simulations are illustrative — not clinical advice
        """)

        st.info("Tip: Keep this guide open while you explore the first few modules.")

    # ── Interactive Viral Load Demo ──────────────────────
    st.subheader("Quick Viral Load Demo")
    st.caption("Adjust parameters to see simulated viral suppression (toy model for illustration)")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        drug_pressure = st.slider(
            "Drug Pressure (0 = none, 1 = maximum)",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.05,
            help="Higher values represent stronger treatment effect."
        )

        enable_gene = st.checkbox("Enable Gene Editing (e.g. CCR5 knockout)", value=False)
        gene_effect = st.slider(
            "Gene Editing Effectiveness",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            disabled=not enable_gene,
            help="Fraction of cells successfully edited."
        ) if enable_gene else 0.0

    with col_right:
        DAYS = 120
        t = np.linspace(0, DAYS, 200)
        # Very simplified exponential decay model (placeholder – real model in resistance/host modules)
        viral_load = np.exp(-0.05 * t) * (1 + 1.5 * (1 - drug_pressure)) * (1 + 0.8 * (1 - gene_effect))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t, y=viral_load,
            mode='lines',
            line=dict(color='#FF9800', width=3),
            name="Relative Viral Load"
        ))
        fig.update_layout(
            title="Simulated Viral Load Trajectory",
            xaxis_title="Time (days)",
            yaxis_title="Relative Viral Load (log scale recommended for real use)",
            template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white",
            height=420,
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Available Drugs ──────────────────────────────────
    st.subheader("Drugs Available in Simulations")
    st.write(", ".join([f"**{drug}**" for drug in REAL_DRUGS]))

    # ── Features & Goals ─────────────────────────────────
    cols = st.columns(2)
    with cols[0]:
        st.markdown("### Key Features")
        st.markdown("""
        • Multi-drug resistance simulation  
        • Host protein & gene editing modeling  
        • Interactive knowledge graph + GNN  
        • 3D viral particle visualization  
        • AI-powered explanations  
        • Scenario comparison & export
        """)

    with cols[1]:
        st.markdown("### Research Goals")
        st.markdown("""
        • Safe hypothesis testing environment  
        • Explore viral dynamics under pressure  
        • Evaluate gene editing potential  
        • Support drug combination & repurposing ideas  
        • Generate publication-grade visuals & insights
        """)

# ───────────────────────────────────────────────
# Other Modules (with explainability where relevant)
# ───────────────────────────────────────────────
elif selected == "🧬 Resistance Engine":
    resistance_engine()
    with st.expander("Explainable Insights", expanded=False):
        explainability_panel()

elif selected == "🧠 Host-Protein Suppression":
    host_protein_model()
    with st.expander("Explainable Insights", expanded=False):
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
# Global Footer
# ───────────────────────────────────────────────
st.markdown("---")
footer_html = f"""
<div style='text-align:center; color:#78909c; font-size:0.9rem; padding:1rem;'>
    V-HIVRAP v{st.session_state.app_version} • Research simulation tool • 
    Developed by Simon • Contact: <a href='mailto:allin@gmail.com'>allin@gmail.com</a>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)