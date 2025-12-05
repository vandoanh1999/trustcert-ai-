"""
Genesis Core V8: Real-Time Network Dashboard

This Streamlit application provides a live (simulated) view into the
health and performance of the Genesis P2P network.
"""
import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Genesis Network Dashboard", layout="wide")

st.title("🔴 Live Genesis Network Dashboard")

# --- Helper Functions to Generate Mock Data ---
def get_mock_nodes():
    """Generates a list of mock node data."""
    nodes = []
    # 3 Super Nodes
    for i in range(3):
        nodes.append({
            "Node ID": f"node_{i+1}", "Tier": "SUPER_NODE", "Trust": round(0.8 + random.random() * 0.19, 3),
            "Contribution": round(random.random() * 100 + 50, 2), "Uptime (H)": round(random.random() * 100 + 24, 1),
            "Mock Earnings": round(random.random() * 50, 4)
        })
    # 5 Stable Nodes
    for i in range(5):
        nodes.append({
            "Node ID": f"node_{i+4}", "Tier": "STABLE", "Trust": round(0.6 + random.random() * 0.15, 3),
            "Contribution": round(random.random() * 40 + 10, 2), "Uptime (H)": round(random.random() * 50, 1),
            "Mock Earnings": round(random.random() * 10, 4)
        })
    return pd.DataFrame(nodes)

def get_network_health():
    """Generates mock network health metrics."""
    return {
        "Total Nodes": 25,
        "Super Nodes Online": 3,
        "Transactions per Second (TPS)": round(random.random() * 10 + 15, 2),
        "Active Proposals": random.randint(1, 5),
        "Network Health": "✅ Operational"
    }

# --- Dashboard Layout ---
placeholder = st.empty()

while True:
    with placeholder.container():

        health_metrics = get_network_health()

        # --- Header Metrics ---
        st.header("Network At-a-Glance")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(label="Network Health", value=health_metrics["Network Health"])
        kpi2.metric(label="Total Nodes", value=health_metrics["Total Nodes"])
        kpi3.metric(label="Super Nodes Online", value=f"{health_metrics['Super Nodes Online']} / 3")
        kpi4.metric(label="Transactions per Second", value=health_metrics["Transactions per Second (TPS)"])

        st.divider()

        # --- Leaderboards & Tables ---
        col1, col2 = st.columns([2, 1])

        with col1:
            st.header("Super Node Leaderboard")
            node_df = get_mock_nodes()
            super_nodes = node_df[node_df['Tier'] == 'SUPER_NODE'].sort_values("Contribution", ascending=False).reset_index(drop=True)
            st.dataframe(super_nodes, use_container_width=True)

            st.header("Recent Network Activity")
            activity_data = {
                "Timestamp": [f"{time.strftime('%H:%M:%S')}"]*5,
                "Type": ["PROPOSAL_VOTE", "NEW_EXPERT_PROPOSAL", "REPUTATION_GOSSIP", "NODE_ANNOUNCE", "PROPOSAL_VOTE"],
                "Source Node": [f"node_{random.randint(1,3)}" for _ in range(5)],
                "Details": [
                    "Voted YES on prop_geo_v1", "expert_geology_v1 proposed by node_18", "Gossiped 5 reputation updates",
                    "node_25 announced with fingerprint abc...", "Voted YES on prop_geo_v1"
                ]
            }
            st.table(pd.DataFrame(activity_data))

        with col2:
            st.header("Stable Node Pool")
            stable_nodes = node_df[node_df['Tier'] == 'STABLE']
            st.dataframe(stable_nodes, use_container_width=True)

            st.header("Active Proposals")
            st.info(f"**prop_geology_v1**\n- Approval: 55%\n- Voters: 2/3")
            st.warning(f"**prop_finance_v3**\n- Approval: 15%\n- Voters: 1/3")

        time.sleep(2)
