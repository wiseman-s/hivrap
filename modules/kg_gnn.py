# modules/kg_gnn.py
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import streamlit.components.v1 as components
from datetime import datetime

# Data (unchanged)
DRUG_TARGET_MUTATIONS = {
    "Tenofovir": {
        "target": "Reverse Transcriptase",
        "mutations": ["K65R", "K70E", "Y115F", "M184V"]
    },
    "Lamivudine": {
        "target": "Reverse Transcriptase",
        "mutations": ["M184V", "M184I", "K65R", "L74V"]
    },
    "Dolutegravir": {
        "target": "Integrase",
        "mutations": ["R263K", "G118R", "E138K", "Q148H", "N155H"]
    },
    "Efavirenz": {
        "target": "Reverse Transcriptase",
        "mutations": ["K103N", "Y181C", "G190A", "K101E"]
    }
}

def kg_gnn_module():
    st.subheader("Knowledge Graph + GNN")
    st.markdown("Drug → Target → Resistance Mutation Network")

    selected_drugs = st.multiselect(
        "Select drugs to visualize",
        list(DRUG_TARGET_MUTATIONS.keys()),
        default=["Tenofovir", "Dolutegravir"]
    )

    if not selected_drugs:
        st.info("Select drugs to build the graph.")
        return

    # Build simple NetworkX graph
    G = nx.Graph()
    for drug in selected_drugs:
        if drug not in DRUG_TARGET_MUTATIONS:
            continue
        info = DRUG_TARGET_MUTATIONS[drug]
        target = info["target"]

        G.add_node(drug, type="Drug")
        G.add_node(target, type="Target")
        G.add_edge(drug, target, title="inhibits")

        for mut in info["mutations"]:
            G.add_node(mut, type="Mutation")
            G.add_edge(target, mut, title="confers resistance to")

    if len(G.nodes) == 0:
        st.warning("No connections for selected drugs.")
        return

    # Debug toggle
    use_static_fallback = st.checkbox("Use static fallback (matplotlib) instead of interactive pyvis", value=False)

    if use_static_fallback:
        st.info("Showing static fallback view (non-interactive).")
        fig, ax = plt.subplots(figsize=(10, 8))
        pos = nx.spring_layout(G, seed=42)
        
        # Color by type
        colors = []
        for node, data in G.nodes(data=True):
            if data["type"] == "Drug": colors.append("#ffdd57")
            elif data["type"] == "Target": colors.append("#44ff88")
            else: colors.append("#ff6666")

        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=800, font_size=10, ax=ax)
        ax.set_title("Static Network Fallback")
        st.pyplot(fig)
        return

    # Pyvis interactive attempt
    try:
        net = Network(
            height="650px",
            width="100%",
            notebook=False,
            bgcolor="#222222",
            font_color="white",
            directed=False,
            cdn_resources='in_line'  # Embed everything – no external loads
        )

        # Strong stabilization + fit to view
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -8000,
              "springLength": 200,
              "springConstant": 0.04
            },
            "stabilization": {
              "enabled": true,
              "iterations": 2000,
              "fit": true
            }
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
          }
        }
        """)

        # Add nodes/edges
        for node, attrs in G.nodes(data=True):
            color = "#ffdd57" if attrs["type"] == "Drug" else "#44ff88" if attrs["type"] == "Target" else "#ff6666"
            title = f"{attrs['type']}: {node}"
            net.add_node(node, label=node, color=color, title=title)

        for src, dst in G.edges():
            net.add_edge(src, dst)

        # Direct HTML generation + embed
        html_string = net.generate_html(notebook=False)
        components.html(html_string, height=700)

        st.caption("**Controls** (top-left of graph area): zoom/pan with mouse/buttons, hover for info.")

    except Exception as e:
        st.error(f"Pyvis failed: {str(e)}")
        st.info("Falling back to static view below. Try: Chrome browser, update pyvis (`pip install --upgrade pyvis`), or check browser console (F12) for JS errors.")

        # Static fallback if pyvis crashes
        fig, ax = plt.subplots(figsize=(10, 8))
        pos = nx.spring_layout(G, seed=42)
        colors = ["#ffdd57" if d["type"] == "Drug" else "#44ff88" if d["type"] == "Target" else "#ff6666" for _, d in G.nodes(data=True)]
        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=800, font_size=10, ax=ax)
        st.pyplot(fig)

    # Capture button (unchanged)
    if st.button("Capture this view to Comparator"):
        sim_id = len(st.session_state.get("simulations", [])) + 1
        name = f"KG – {', '.join(selected_drugs)} ({datetime.now().strftime('%H:%M')})"
        st.session_state.setdefault("simulations", []).append({
            "id": sim_id,
            "module": "Knowledge Graph + GNN",
            "name": name,
            "params": {"selected_drugs": selected_drugs[:]},
            "data": None,
            "timestamp": str(datetime.now())
        })
        st.success("Captured → check Scenario Comparator")