import streamlit as st
import time
import os
import textwrap
import pandas as pd
from data import get_available_projects, load_status, load_events, get_artifacts_list, get_aggregated_metrics, get_all_findings
from graph import render_pipeline_graph
from components import (
    render_pipeline_ribbon,
    render_system_health,
    render_scorecards,
    render_agent_cards,
    render_activity_feed
)
from agent_registry import AGENTS, get_agent_by_id
from insights import render_insights_dashboard
import ui.explorer as explorer

from ui.styles import load_css

st.set_page_config(
    page_title="Cloud Assessment Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INJECT HSBC ENTERPRISE STYLING ---
load_css()

# Sidebar
st.sidebar.title("Platform Navigation")
projects = get_available_projects()

if not projects:
    st.sidebar.warning("No projects found.")
    st.stop()
    
# Clean Sidebar Controls
st.sidebar.markdown("### Context")
selected_project = st.sidebar.selectbox("Active Project", projects)

st.sidebar.markdown("---")
st.sidebar.markdown("### Controls")
auto_refresh = st.sidebar.checkbox("Live Polling", value=True)
if auto_refresh:
    time.sleep(2)
    st.rerun()

# Load Data
status = load_status(selected_project)
events = load_events(selected_project, limit=500)
metrics = get_aggregated_metrics(selected_project)
findings = get_all_findings(selected_project) # New Aggregation

if not status:
    st.error(f"System Error: Could not load status for {selected_project}")
    st.stop()

# --- M11: Enterprise Header ---
c_head_1, c_head_2 = st.columns([3, 1])
with c_head_1:
    st.title(f"Cloud Architecture Assessment: {selected_project}")
    st.markdown("Use the dashboard below to review portfolio health, governance findings, and delivery planning.")

with c_head_2:
    # Status Badge in Header
    overall = status.get('overall', {}).get('status', 'UNKNOWN')
    color = "#DB0011" if overall == "FAILED" else "#1E7E34"
    st.markdown(textwrap.dedent(f"""
    <div style="text-align: right; padding-top: 10px;">
        <span style="background: {color}; color: white; padding: 5px 10px; font-weight: bold; font-size: 14px;">STATUS: {overall}</span>
    </div>
    """), unsafe_allow_html=True)

st.markdown("---")

# Pipeline Ribbon (Always Visible)
render_pipeline_ribbon(status)
st.markdown("---")

# --- Tabs Layer ---
# UPDATED TABS LIST
tabs = st.tabs(["Overview", "Results Explorer", "Executive Insights", "Agent Catalog", "Live Console", "Drill-down", "Flow"])

# Tab 1: Overview
with tabs[0]:
    render_system_health(status, 0) # Failures count placeholder
    render_scorecards(metrics)
    st.markdown("### Operational Status")
    render_agent_cards(status)

# Tab 2: Results Explorer (M13 New)
with tabs[1]:
    explorer.render(selected_project, status, findings)

# Tab 3: Executive Insights (M10 New)
with tabs[2]:
    # Pass full status data as proxy for governance data if not available separately
    # In reality, we should load governance_summary.json directly here or via data loader
    # Using 'status' which has repo info, but metrics are better passed directly
    # Re-using get_aggregated_metrics isn't enough for the lists. 
    # Let's verify we have governance data
    import data
    gov_data_path = f"outputs/{selected_project}/governance_summary.json"
    if os.path.exists(gov_data_path):
        import json
        with open(gov_data_path, 'r') as f:
            gov_data = json.load(f)
    else:
        gov_data = {}
        
    render_insights_dashboard(metrics, gov_data)

# Tab 4: Agent Catalog (M7 New)
with tabs[3]:
    st.subheader("Agent Capability Catalog")
    
    agent_data = []
    for a in AGENTS:
        agent_data.append({
            "Icon": a["icon"],
            "Agent": a["display_name"],
            "Category": a["category"],
            "Purpose": a.get("purpose", ""),
            "Inputs": ", ".join(a.get("inputs", [])),
            "Outputs": ", ".join(a.get("outputs", []))
        })
    st.table(pd.DataFrame(agent_data))

# Tab 5: Live Console
with tabs[4]:
    render_activity_feed(events)

# Tab 6: Drill-down & Timeline (M7 Enhanced)
with tabs[5]:
    st.subheader("Agent Inspector")
    
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        agent_options = [a["display_name"] for a in AGENTS if not a.get("future")]
        selected_agent_name = st.selectbox("Select Agent", agent_options)
        selected_agent = next((a for a in AGENTS if a["display_name"] == selected_agent_name), None)
        
    with col_info:
        if selected_agent:
            st.info(f"**{selected_agent['icon']} {selected_agent['display_name']}**\n\n{selected_agent['short_desc']}")

    if selected_agent:
        st.markdown("### Execution Timeline")
        
        # Filter events for this agent by ID (New M7) or Stage fallback
        agent_events = [e for e in events if e.get("meta", {}).get("agent_id") == selected_agent["id"] or e.get("stage") in selected_agent["stages"]]
        
        if agent_events:
            # Calculate Duration
            start_event = next((e for e in reversed(agent_events) if e["status"] == "STARTED"), None)
            end_event = next((e for e in agent_events if e["status"] in ["COMPLETED", "FAILED"]), None)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Status", end_event["status"] if end_event else "IN PROGRESS")
            if start_event:
                c2.text(f"Started: {start_event['ts'].split('T')[1][:8]}")
            if end_event and start_event:
                # Simple duration calc (naive)
                c3.text(f"Ended: {end_event['ts'].split('T')[1][:8]}")
            
            st.markdown("#### Event Log")
            st.table(pd.DataFrame(agent_events)[["ts", "status", "message", "repo"]])
            
            st.markdown("#### Produced Artifacts")
            all_artifacts = []
            for e in agent_events:
                if e.get("artifact_paths"):
                    all_artifacts.extend(e["artifact_paths"])
            
            if all_artifacts:
                for path in list(set(all_artifacts)):
                    st.code(path, language="bash")
            else:
                st.info("No artifacts produced yet.")
        else:
            st.warning("No execution data found for this agent.")

# Tab 6: Flow
with tabs[5]:
    st.subheader("Pipeline Flow")
    try:
        graph = render_pipeline_graph(status)
        st.graphviz_chart(graph)
    except Exception as e:
        st.error(f"Graphviz error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption(f"v1.2 AgentOps | {selected_project}")
