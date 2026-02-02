import streamlit as st
import json
import os
import random

SCENARIO_DIRS = {
    "Resistance Engine": "resistance_scenarios",
    "Host-Protein Suppression": "saved_scenarios",
    "VR / Advanced Visualization": "vr_scenarios",
    "Knowledge Graph + GNN": "kg_scenarios"
}

def ai_explain():
    st.subheader("💡 AI Research Assistant")
    st.write("Explains simulations dynamically based on selected drugs, gene editing, and patient scenarios.")

    module_choice = st.selectbox("Select Module to Explain", list(SCENARIO_DIRS.keys()))
    scenario_dir = SCENARIO_DIRS[module_choice]
    os.makedirs(scenario_dir, exist_ok=True)
    saved_files = [f for f in os.listdir(scenario_dir) if f.endswith(".json")]
    selected_scenario = st.selectbox("Select Scenario", ["None"] + saved_files) if saved_files else "None"

    params = {}
    if selected_scenario != "None":
        with open(os.path.join(scenario_dir, selected_scenario), "r") as f:
            params = json.load(f)
        st.success(f"Scenario '{selected_scenario}' loaded!")

    explanations = []
    if module_choice == "Resistance Engine":
        drugs = params.get("selected_drugs", ["Tenofovir"])
        dp = params.get("drug_pressure", 0.6)
        adherence = params.get("adherence", 0.8)
        mutation_rate = params.get("mutation_rate", 0.01)
        explanations.append(f"Selected drugs ({', '.join(drugs)}) with drug pressure {dp} and adherence {adherence} influence resistance evolution. Mutation rate: {mutation_rate}.")

    elif module_choice == "Host-Protein Suppression":
        drugs = params.get("selected_drugs", ["Tenofovir"])
        host = params.get("host_activity", 0.5)
        gene_editing = params.get("gene_editing", False)
        gene_effect = params.get("gene_effect", 0.5)
        comorbidities = [c for c, v in [('Diabetes', params.get('diabetes', False)), 
                                        ('Hypertension', params.get('hypertension', False)), 
                                        ('Obesity', params.get('obesity', False))] if v]
        explanations.append(f"Virtual patient taking ({', '.join(drugs)}). Host-protein activity: {host}.")
        if gene_editing: explanations.append(f"Gene editing enabled, effectiveness {gene_effect}.")
        if comorbidities: explanations.append(f"Comorbidities: {', '.join(comorbidities)}.")
        explanations.append("These factors influence viral suppression dynamics.")

    elif module_choice == "VR / Advanced Visualization":
        drugs = params.get("selected_drugs", ["Tenofovir"])
        gene_editing = params.get("gene_editing", False)
        gene_effect = params.get("gene_effect", 0.5)
        drug_eff = params.get("drug_effectiveness", 0.6)
        explanations.append(f"3D simulation with drugs: {', '.join(drugs)}. Drug effectiveness: {drug_eff}.")
        if gene_editing: explanations.append(f"Gene editing enabled, effectiveness {gene_effect}.")
        explanations.append("Particle colors show viral activity and suppression.")

    elif module_choice == "Knowledge Graph + GNN":
        highlighted = params.get("highlight_drugs", ["Tenofovir"])
        explanations.append(f"Highlighted drugs: {', '.join(highlighted)}. Interactions with targets and mutations are emphasized.")

    if explanations:
        st.success(random.choice(explanations))
    else:
        st.info("No scenario loaded. Select a saved scenario for AI explanation.")
    st.info("AI interprets scenarios based on drugs, gene editing, and patient parameters.")
