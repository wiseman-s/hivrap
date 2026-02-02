import streamlit as st
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go

from .explainable_ai import explainability_panel  # relative import

def target_cell_model(y, t, beta_eff, delta, p, c, lambda_, d_T):
    """Classic target-cell limited HIV model with effective infectivity beta_eff"""
    T, I, V = y
    dT_dt = lambda_ - d_T * T - beta_eff * V * T
    dI_dt = beta_eff * V * T - delta * I
    dV_dt = p * I - c * V
    return [dT_dt, dI_dt, dV_dt]

def host_protein_model():
    st.subheader("🧬 Host-Protein Suppression & Virtual Patient Simulation")

    # ── Parameters (defaults from literature-ish values) ────────
    default_params = {
        "selected_drugs": ["Tenofovir"],
        "host_activity": 0.5,         # 0–1 scalar on immune/host suppression
        "adherence": 0.8,
        "drug_pressure": 0.6,
        "gene_editing": False,
        "gene_effect": 0.5,
        "diabetes": False,
        "hypertension": False,
        "obesity": False,
        "duration": 120
    }

    # Session state for this module's current run
    if "host_params" not in st.session_state:
        st.session_state.host_params = default_params.copy()

    params = st.session_state.host_params

    # ── Inputs ────────────────────────────────────────────────
    with st.expander("Simulation Settings", expanded=True):
        params["selected_drugs"] = st.multiselect("Drugs", ["Tenofovir", "Lamivudine", "Dolutegravir", "Efavirenz"], default=params["selected_drugs"])
        col1, col2 = st.columns(2)
        with col1:
            params["drug_pressure"] = st.slider("Drug Pressure", 0.0, 1.0, params["drug_pressure"], help="Combined ARV effect")
            params["host_activity"] = st.slider("Host Immune/Activity Level", 0.0, 1.0, params["host_activity"])
            params["adherence"] = st.slider("Adherence", 0.0, 1.0, params["adherence"])
        with col2:
            params["gene_editing"] = st.checkbox("Gene Editing (e.g. CCR5)", params["gene_editing"])
            if params["gene_editing"]:
                params["gene_effect"] = st.slider("Editing Effectiveness", 0.0, 1.0, params["gene_effect"])
            params["duration"] = st.slider("Days", 50, 300, params["duration"])

        st.markdown("**Comorbidities** (increase viral fitness)")
        col3, col4, col5 = st.columns(3)
        with col3: params["diabetes"]     = st.checkbox("Diabetes",     params["diabetes"])
        with col4: params["hypertension"] = st.checkbox("Hypertension", params["hypertension"])
        with col5: params["obesity"]      = st.checkbox("Obesity",      params["obesity"])

    # ── Run Simulation Button ────────────────────────────────
    if st.button("Run Simulation", type="primary"):
        # Simplified drug + gene + host effect on infectivity & production
        beta_base = 2.5e-4     # ml/day (literature range)
        drug_eff = params["drug_pressure"] * params["adherence"]
        gene_sup = params["gene_effect"] if params["gene_editing"] else 0.0
        beta_eff = beta_base * (1 - 0.8 * drug_eff) * (1 - 0.7 * gene_sup)  # rough reductions

        comorbidity_boost = 1.0
        if params["diabetes"]:     comorbidity_boost *= 1.20
        if params["hypertension"]: comorbidity_boost *= 1.15
        if params["obesity"]:      comorbidity_boost *= 1.10

        p_eff = 5000 * comorbidity_boost   # virions/cell/day
        delta = 0.7                         # infected cell death /day
        c = 5.0                             # virus clearance /day
        lambda_ = 1e4                       # target cell production
        d_T = 0.01                          # target cell death

        # Initial conditions (acute-like start)
        T0 = 1e6
        I0 = 1e-3 * T0
        V0 = 1e-1
        y0 = [T0, I0, V0]

        t = np.linspace(0, params["duration"], 300)

        sol = odeint(target_cell_model, y0, t, args=(beta_eff, delta, p_eff, c, lambda_, d_T))

        # Store in session state for comparator
        st.session_state.simulations.append({
            "id": len(st.session_state.simulations) + 1,
            "module": "Host-Protein Suppression",
            "name": f"Host {len(st.session_state.simulations)+1}",
            "params": params.copy(),
            "data": {"t": t.tolist(), "T": sol[:,0].tolist(), "I": sol[:,1].tolist(), "V": sol[:,2].tolist()},
            "timestamp": str(np.datetime64('now'))
        })

        st.success("Simulation completed → added to Scenario Comparator!")

    # ── Plot (if data exists) ────────────────────────────────
    if "simulations" in st.session_state and st.session_state.simulations:
        last = st.session_state.simulations[-1]
        if last["module"] == "Host-Protein Suppression":
            t = np.array(last["data"]["t"])
            V = np.array(last["data"]["V"])

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t, y=V, mode='lines', name='Virus (copies/ml)', line=dict(color='orange', width=3)))
            fig.add_trace(go.Scatter(x=t, y=last["data"]["T"], mode='lines', name='Target Cells', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=t, y=last["data"]["I"], mode='lines', name='Infected Cells', line=dict(color='red')))

            fig.update_layout(
                title="Within-Host Dynamics (Target-Cell Limited Model)",
                xaxis_title="Time (days)",
                yaxis_title="Concentration (log scale)",
                yaxis_type="log",
                template="plotly_dark",
                height=500,
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

    explainability_panel(context_params=params)

    # Summary
    with st.expander("Virtual Patient Summary"):
        st.write(f"**Drugs:** {', '.join(params['selected_drugs'])}")
        st.write(f"**Effective Drug + Adherence:** {params['drug_pressure']*params['adherence']:.2f}")
        st.write(f"**Host Activity:** {params['host_activity']:.2f}")
        if params['gene_editing']: st.write(f"**Gene Editing Effect:** {params['gene_effect']:.2f}")
        comorb = [k for k,v in params.items() if k in ["diabetes","hypertension","obesity"] and v]
        st.write(f"**Comorbidities:** {', '.join(comorb) or 'None'}")