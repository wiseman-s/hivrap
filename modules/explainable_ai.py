import streamlit as st
import numpy as np
import plotly.graph_objects as go

def explainability_panel(context_params: dict = None):
    """
    Improved explainable panel: shows pseudo feature importance based on actual simulation params.
    context_params: dict from the calling module (e.g. {'drug_pressure': 0.7, 'gene_editing': True, ...})
    """
    st.subheader("🧠 Explainable Insights")

    if not context_params:
        st.info("No simulation parameters available yet. Run a scenario to see insights.")
        return

    # Pseudo-importance: heuristic mapping from params (0–1 normalized)
    # In real version → use SHAP/LIME on a surrogate model
    importance = {}

    # Common factors
    importance["Drug Pressure"] = context_params.get("drug_pressure", 0.5)
    importance["Adherence"] = context_params.get("adherence", 0.8)
    
    # Module-specific
    if "host_activity" in context_params:
        importance["Host Protein Activity"] = context_params["host_activity"]
    if "gene_editing" in context_params and context_params["gene_editing"]:
        importance["Gene Editing Effect"] = context_params.get("gene_effect", 0.5)
    if "mutation_rate" in context_params:
        importance["Mutation Rate"] = context_params["mutation_rate"]
    if "diabetes" in context_params and context_params["diabetes"]:
        importance["Diabetes Comorbidity"] = 0.75
    if "hypertension" in context_params and context_params["hypertension"]:
        importance["Hypertension Comorbidity"] = 0.65

    if not importance:
        st.warning("No key parameters detected for explanation.")
        return

    features = list(importance.keys())
    values = np.array(list(importance.values()))
    sorted_idx = np.argsort(values)[::-1]
    features = [features[i] for i in sorted_idx]
    values = values[sorted_idx]

    # Bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values,
        y=features,
        orientation='h',
        marker=dict(color=values, colorscale='Viridis', showscale=True),
        text=np.round(values, 2),
        textposition='auto'
    ))

    fig.update_layout(
        title="Relative Influence of Key Factors",
        xaxis_title="Influence Score (heuristic)",
        yaxis_title="Factor",
        height=350 + 30 * len(features),
        template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Top Influences")
    for feat, val in zip(features[:3], values[:3]):
        if val > 0.75:
            st.success(f"**{feat}** – very strong influence ({val:.2f})")
        elif val > 0.5:
            st.info(f"**{feat}** – moderate to strong ({val:.2f})")
        else:
            st.warning(f"{feat} – lower influence ({val:.2f})")

    st.caption("Note: Scores are heuristic based on parameters. Future versions can use SHAP/LIME on surrogate ML models.")