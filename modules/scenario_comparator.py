import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Directories of scenarios from all modules
SCENARIO_DIRS = {
    "Resistance Engine": "resistance_scenarios",
    "Host-Protein Suppression": "saved_scenarios",
    "VR / Advanced Visualization": "vr_scenarios"
}

def scenario_comparator():
    st.subheader("📊 Multi-Scenario Comparison")

    # --- Select Module ---
    module_choice = st.selectbox("Select Module to Compare", list(SCENARIO_DIRS.keys()))
    scenario_dir = SCENARIO_DIRS[module_choice]
    os.makedirs(scenario_dir, exist_ok=True)
    saved_files = [f for f in os.listdir(scenario_dir) if f.endswith(".json")]
    if not saved_files:
        st.info("No saved scenarios in this module.")
        return

    selected_files = st.multiselect("Select Scenarios to Compare", saved_files, default=saved_files[:2])
    if not selected_files:
        st.warning("Select at least one scenario to compare.")
        return

    # --- Load Scenarios ---
    scenarios = []
    for f in selected_files:
        with open(os.path.join(scenario_dir, f), "r") as file:
            params = json.load(file)
            params['filename'] = f
            scenarios.append(params)

    # --- Comparison Plot ---
    st.markdown("### Comparative Viral Load / Resistance Simulation")
    fig = go.Figure()
    duration = 100
    t = np.arange(0, duration)

    for scenario in scenarios:
        if module_choice == "Host-Protein Suppression":
            viral_load = np.exp(t / 25)
            comorbidity_factor = 1.0
            if scenario.get('diabetes'): comorbidity_factor *= 1.2
            if scenario.get('hypertension'): comorbidity_factor *= 1.15
            if scenario.get('obesity'): comorbidity_factor *= 1.1
            viral_load *= comorbidity_factor
            viral_load *= (1 - scenario.get("host_activity",0.5)*scenario.get("drug_pressure",0.6)*scenario.get("adherence",0.8))
            viral_load *= (1 - scenario.get("gene_effect",0.5) if scenario.get("gene_editing",False) else 1)
            fig.add_trace(go.Scatter(x=t, y=viral_load, mode='lines', name=scenario['filename']))

        elif module_choice == "Resistance Engine":
            t_res = np.arange(0, scenario.get("duration",100))
            for drug in scenario.get("selected_drugs", ["Tenofovir"]):
                dp = scenario.get("drug_pressure",0.6) * np.random.uniform(0.8,1.2)
                mu = scenario.get("mutation_rate",0.01) * np.random.uniform(0.8,1.2)
                res = np.exp(mu*dp*t_res)*(1-scenario.get("adherence",0.8))
                fig.add_trace(go.Scatter(x=t_res, y=res, mode='lines', name=f"{scenario['filename']} | {drug}"))

        elif module_choice == "VR / Advanced Visualization":
            num_particles = scenario.get("num_particles",50)
            colors = scenario.get("selected_drugs", ["Tenofovir"])
            fig.add_trace(go.Scatter(x=np.arange(num_particles), y=np.random.rand(num_particles), mode='markers', name=scenario['filename']))

    fig.update_layout(
        title=f"Scenario Comparison – {module_choice}",
        xaxis_title="Time / Particles",
        yaxis_title="Viral Load / Resistance Index",
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Export Options ---
    st.markdown("### Export Scenarios")
    export_type = st.radio("Select Export Type", ["CSV", "JSON"])
    if st.button("Export Selected Scenarios"):
        export_data = []
        for scenario in scenarios:
            export_data.append({k:v for k,v in scenario.items() if k != 'filename'})
        if export_type == "CSV":
            df = pd.DataFrame(export_data)
            df.to_csv("exported_scenarios.csv", index=False)
            st.success("Exported scenarios to exported_scenarios.csv")
        else:
            with open("exported_scenarios.json","w") as f:
                json.dump(export_data,f, indent=4)
            st.success("Exported scenarios to exported_scenarios.json")
