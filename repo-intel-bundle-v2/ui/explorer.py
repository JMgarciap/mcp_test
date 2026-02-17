import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ui.components import render_system_health # Re-use if needed
from ui.agent_registry import AGENTS

def render_finding_card(finding):
    """
    Renders a single finding in a professional 'Consulting' style card.
    Splunk/Datadog inspired.
    """
    severity = finding.get('severity', 'MEDIUM')
    color = "#F58220" # Orange
    if severity == "HIGH" or severity == "CRITICAL": color = "#D93F3C"
    elif severity == "LOW": color = "#5CC151"
    
    # CSS class based on severity for left-border
    border_class = f"border-{severity.lower()}"
    
    html = f"""
    <div class="finding-card" style="border-left: 5px solid {color};">
        <div class="finding-header">
            <div>
                <span class="finding-badge" style="background-color: {color};">{severity}</span>
                <span style="color: #888; font-size: 11px; margin-left: 10px; text-transform: uppercase;">{finding.get('category', 'General')}</span>
            </div>
            <div style="font-size: 11px; color: #666;">{finding.get('agent', 'System')}</div>
        </div>
        <div class="finding-title">{finding.get('title')}</div>
        <div class="finding-desc">{finding.get('description')}</div>
        
        <div class="finding-remediation">
            <strong style="color: #F58220;">REMEDIATION:</strong> {finding.get('remediation')}
        </div>
        <div class="finding-meta">
            <span>Repo: <strong>{finding.get('repo')}</strong></span>
            <span>File: {finding.get('file')} : {finding.get('line')}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_agent_view(findings):
    """
    Groups findings by Agent and shows stats.
    """
    st.markdown("#### Agent Intelligence")
    
    # Group by Agent
    agent_groups = {}
    for f in findings:
        agent = f.get('agent', 'Unknown')
        if agent not in agent_groups: agent_groups[agent] = []
        agent_groups[agent].append(f)
        
    # Selector
    selected_agent = st.selectbox("Select Agent Context", list(agent_groups.keys()) if agent_groups else ["No Data"])
    
    if selected_agent != "No Data":
        agent_findings = agent_groups[selected_agent]
        
        # Stats Row
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Findings", len(agent_findings))
        high_sev = len([f for f in agent_findings if f['severity'] in ['HIGH', 'CRITICAL']])
        c2.metric("Critical Risks", high_sev)
        c3.metric("Affected Repos", len(set(f['repo'] for f in agent_findings)))
        
        st.divider()
        
        # Findings List
        for f in agent_findings:
            render_finding_card(f)

def render_repo_view(findings):
    """
    Groups findings by Repository.
    """
    st.markdown("#### Repository Deep Dive")
    repo_groups = {}
    for f in findings:
        repo = f.get('repo', 'Unknown')
        if repo not in repo_groups: repo_groups[repo] = []
        repo_groups[repo].append(f)
        
    selected_repo = st.selectbox("Select Repository", list(repo_groups.keys()) if repo_groups else ["No Data"])
    
    if selected_repo != "No Data":
        repo_data = repo_groups[selected_repo]
        st.caption(f"Showing {len(repo_data)} findings for {selected_repo}")
        for f in repo_data:
            render_finding_card(f)

def render_risk_view(findings):
    """
    Heatmap / Matrix view of risks.
    """
    st.markdown("#### Risk Matrix")
    
    # Simple Matrix: Severity vs Category
    df = pd.DataFrame(findings)
    if not df.empty:
        # Check if 'category' column exists
        if 'category' not in df.columns:
            df['category'] = 'General'
            
        pivot = df.pivot_table(index='severity', columns='category', aggfunc='size', fill_value=0)
        st.dataframe(pivot, use_container_width=True)
        
        # List High Risks
        st.markdown("##### Critical Actions Required")
        high_risks = [f for f in findings if f.get('severity') in ['HIGH', 'CRITICAL']]
        for f in high_risks:
            render_finding_card(f)
    else:
        st.info("No findings data available for risk analysis.")

def render(project_name, aggregated_data, findings):
    """
    Main Entry Point for Results Explorer Tab
    """
    st.markdown("## 🔎 Results Intelligence Center")
    
    # 1. Top Bar: View Selector and Global Filters
    col_view, col_filter = st.columns([1, 2])
    
    with col_view:
        view_mode = st.radio("Intelligence View", ["Agent", "Repository", "Risk", "Execution Flow"], horizontal=True, label_visibility="collapsed")
        
    with col_filter:
        # Quick Filters
        st.caption("Global Filters")
        f_sev = st.multiselect("Severity", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH", "MEDIUM"], label_visibility="collapsed", placeholder="Filter by Severity")
        
    # Apply Filters
    filtered_findings = [f for f in findings if f.get('severity') in f_sev]
    
    st.divider()
    
    # 2. Render Selected View
    if view_mode == "Agent":
        render_agent_view(filtered_findings)
    elif view_mode == "Repository":
        render_repo_view(filtered_findings)
    elif view_mode == "Risk":
        render_risk_view(filtered_findings)
    elif view_mode == "Execution Flow":
        st.warning("Execution Flow Intelligence is currently aggregating. Check back after next pipeline run.")
        
