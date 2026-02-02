import streamlit as st
import numpy as np
import plotly.graph_objects as go
from modules.explainable_ai import explainability_panel
import json
import os

SCENARIO_DIR = "resistance_scenarios"
os.makedirs(SCENARIO_DIR, exist_ok=True)

REAL_DRUGS = ["Tenofovir", "Lamivudine", "Dolutegravir", "Efavirenz"]

def resistance_engine():
    st.subheader("Resistance Evolution Engine")
    st.write("Simulate how drug pressure and mutation rates affect viral resistance over time.")

    # Load scenario
    saved_files = [f for f in os.listdir(SCENARIO_DIR) if f.endswith(".json")]
    selected_scenario = st.selectbox("Load Saved Scenario", ["None"] + saved_files) if saved_files else "None"

    params = {
        "selected_drugs": ["Tenofovir"],
        "drug_pressure": 0.6,
        "mutation_rate": 0.01,
        "adherence": 0.8,
        "duration": 100
    }

    if selected_scenario != "None":
        with open(os.path.join(SCENARIO_DIR, selected_scenario), "r") as f:
            params = json.load(f)
        st.success(f"Scenario '{selected_scenario}' loaded!")

    # User inputs
    params["selected_drugs"] = st.multiselect("Select Drugs for Simulation", REAL_DRUGS, default=params["selected_drugs"])
    params["drug_pressure"] = st.slider("Drug Pressure (0=none,1=max)", 0.0, 1.0, params["drug_pressure"])
    params["mutation_rate"] = st.slider("Mutation Rate (per time unit)", 0.001, 0.05, params["mutation_rate"])
    params["adherence"] = st.slider("Patient Adherence Level", 0.0, 1.0, params["adherence"])
    params["duration"] = st.slider("Simulation Duration (days)", 50, 200, params["duration"])

    # Save scenario
    save_name = st.text_input("Save Scenario As (name.json)", "")
    if st.button("Save Scenario"):
        if save_name.endswith(".json") and save_name.strip() != ".json":
            with open(os.path.join(SCENARIO_DIR, save_name), "w") as f:
                json.dump(params, f)
            st.success(f"Scenario saved as '{save_name}'")
        else:
            st.error("Please provide a valid filename ending with .json")

    # Simulation
    t = np.arange(0, params["duration"])
    fig = go.Figure()
    for i, drug in enumerate(params["selected_drugs"]):
        dp = params["drug_pressure"] * np.random.uniform(0.8, 1.2)
        mu = params["mutation_rate"] * np.random.uniform(0.8, 1.2)
        res = np.exp(mu * dp * t) * (1 - params["adherence"])
        fig.add_trace(go.Scatter(x=t, y=res, mode='lines', name=f'{drug} Resistance', line=dict(width=3)))

    fig.update_layout(title="Resistance Evolution Over Time",
                      xaxis_title="Time (days)", yaxis_title="Resistance Index",
                      template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

    explainability_panel()
    st.markdown("### Resistance Scenario Summary")
    st.write(f"**Selected Drugs:** {', '.join(params['selected_drugs'])}")
    st.write(f"**Drug Pressure:** {params['drug_pressure']}")
    st.write(f"**Mutation Rate:** {params['mutation_rate']}")
    st.write(f"**Adherence Level:** {params['adherence']}")
    st.write(f"**Duration:** {params['duration']} days")
