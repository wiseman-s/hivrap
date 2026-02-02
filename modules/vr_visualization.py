import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

SCENARIO_DIR = "vr_scenarios"  # kept for optional future use, but not actively used

def vr_view():
    st.subheader("VR / Advanced Visualization – 3D Viral Particle Simulation")

    st.markdown("""
    Observe a population of viral particles colored by suppression status  
    (red = active, green = drug-suppressed, blue = gene-editing suppressed).
    """)

    # Real drugs – consistent with other modules
    drugs = ["Tenofovir", "Lamivudine", "Dolutegravir", "Efavirenz"]

    # Default / session params
    if "vr_params" not in st.session_state:
        st.session_state.vr_params = {
            "selected_drugs": ["Tenofovir"],
            "gene_editing": False,
            "gene_effect": 0.5,
            "drug_effectiveness": 0.65,
            "num_particles": 80
        }

    params = st.session_state.vr_params

    # Inputs
    with st.expander("Simulation Settings", expanded=True):
        params["selected_drugs"] = st.multiselect(
            "Drugs Applied",
            drugs,
            default=params["selected_drugs"]
        )

        col1, col2 = st.columns(2)
        with col1:
            params["drug_effectiveness"] = st.slider(
                "Drug Suppression Strength",
                0.0, 1.0, params["drug_effectiveness"], 0.05
            )
        with col2:
            params["num_particles"] = st.slider(
                "Number of Viral Particles",
                20, 200, params["num_particles"], 10
            )

        params["gene_editing"] = st.checkbox(
            "Enable Gene Editing Intervention",
            value=params["gene_editing"]
        )
        if params["gene_editing"]:
            params["gene_effect"] = st.slider(
                "Gene Editing Effectiveness",
                0.0, 1.0, params["gene_effect"], 0.05
            )

    # Run / Visualize button
    if st.button("Generate 3D View", type="primary"):
        n = params["num_particles"]

        # Random 3D positions
        x = np.random.uniform(-1, 1, n)
        y = np.random.uniform(-1, 1, n)
        z = np.random.uniform(-1, 1, n)

        # Assign colors based on suppression
        colors = []
        for _ in range(n):
            r = np.random.random()
            if r < params["drug_effectiveness"]:
                colors.append("green")      # suppressed by drugs
            elif params["gene_editing"] and r < params["drug_effectiveness"] + params["gene_effect"]:
                colors.append("blue")       # suppressed by gene editing
            else:
                colors.append("red")        # active / resistant

        fig = go.Figure(data=[go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(
                size=6,
                color=colors,
                opacity=0.85,
                line=dict(width=1, color='rgba(255,255,255,0.4)')
            )
        )])

        fig.update_layout(
            title="3D Viral Particle Population",
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                bgcolor="#0f1117"
            ),
            height=650,
            margin=dict(l=0, r=0, b=0, t=50),
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        **Legend**  
        • **Red** = Active / unsuppressed virus  
        • **Green** = Suppressed by current drugs  
        • **Blue** = Suppressed by gene editing (if enabled)
        """)

        # Auto-add to session state comparator
        sim_id = len(st.session_state.get("simulations", [])) + 1
        name = f"3D Viz – {len(params['selected_drugs'])} drugs ({datetime.now().strftime('%H:%M')})"

        st.session_state.setdefault("simulations", []).append({
            "id": sim_id,
            "module": "VR / Advanced Visualization",
            "name": name,
            "params": params.copy(),
            "data": {
                "colors_count": {
                    "red": colors.count("red"),
                    "green": colors.count("green"),
                    "blue": colors.count("blue")
                }
            },
            "timestamp": str(datetime.now())
        })

        st.success("Visualization added to Scenario Comparator")

    # Summary of last view (optional)
    if "simulations" in st.session_state and st.session_state.simulations:
        last_vr = [s for s in st.session_state.simulations if s["module"] == "VR / Advanced Visualization"]
        if last_vr:
            st.caption(f"Last view: {last_vr[-1]['name']}")