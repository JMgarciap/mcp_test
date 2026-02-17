import streamlit as st
import pandas as pd
import textwrap
import base64
import os
from ui.agent_registry import AGENTS, get_agent_for_stage

def render_pipeline_ribbon(status_data):
    """
    Renders the pipeline status ribbon using the HSBC step indicator style.
    """
    st.markdown("### Process Flow")
    
    stages_status = status_data.get("stages", {})
    
    # n8n-style Flowchart
    html_content = '<div style="display: flex; align-items: center; justify-content: center; overflow-x: auto; padding: 20px 0; gap: 0;">'
    
    agent_count = len(AGENTS)
    
    for i, agent in enumerate(AGENTS):
        # Consolidated Status
        agent_status = "PENDING"
        for stage in agent["stages"]:
            s = stages_status.get(stage, {}).get("status", "PENDING")
            if s == "FAILED":
                agent_status = "FAILED"
                break
            if s == "IN_PROGRESS":
                agent_status = "IN_PROGRESS"
            if s == "COMPLETED" and agent_status != "IN_PROGRESS":
                agent_status = "COMPLETED"

        # Styles
        border_color = "#444"
        icon_color = "#888"
        bg_color = "#212529"
        
        if agent_status == "COMPLETED":
            border_color = "#5CC151"
            icon_color = "#5CC151"
        elif agent_status == "IN_PROGRESS":
            border_color = "#F58220" # Orange
            icon_color = "#F58220"
            bg_color = "#2D3339"
        elif agent_status == "FAILED":
            border_color = "#D93F3C"
            icon_color = "#D93F3C"
        
        # Icon Rendering (Image or Emoji)
        icon_val = agent.get('icon', '🤖')
        icon_html = "🤖" # Default fallback
        
        if icon_val.endswith('.png'):
            try:
                # Construct absolute path to ensure Streamlit finds it
                # Assuming ui/components.py is in repo/ui/, and assets are in repo/ui/assets/
                # We need to go up one level from components.py, or just use relative if running from root
                
                # Best practice: Use path relative to this file
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # icon_val is "ui/assets/repo.png", but we are in "ui/"
                # So if running from root, "ui/assets/repo.png" is correct relative to CWD
                # But let's try to resolve it relative to the script file location
                
                # If icon_val starts with ui/, strip it to get relative from ui folder
                rel_path = icon_val.replace("ui/", "") if icon_val.startswith("ui/") else icon_val
                abs_path = os.path.join(current_dir, rel_path)
                
                if os.path.exists(abs_path):
                    with open(abs_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                        
                    # Status Effects
                    glow_style = f"filter: drop-shadow(0 0 2px {icon_color}); opacity: 0.7;" 
                    if agent_status == "IN_PROGRESS": 
                        glow_style = f"filter: drop-shadow(0 0 8px {icon_color}) brightness(1.2);"
                    elif agent_status == "COMPLETED":
                        glow_style = "filter: none;"
                        
                    icon_html = f'<img src="data:image/png;base64,{encoded_string}" style="width: 120px; height: 120px; object-fit: contain; {glow_style}">'
                else:
                    # Try opening from CWD as fallback
                     with open(icon_val, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                     icon_html = f'<img src="data:image/png;base64,{encoded_string}" style="width: 120px; height: 120px; object-fit: contain;">'
            except Exception:
                icon_html = "🤖" # Final fallback
        else:
             icon_html = f'<div style="font-size: 32px; color: {icon_color};">{icon_val}</div>'

        # Connector Line (Show for all except last one)
        connector_html = ""
        if i < agent_count - 1:
            line_color = "#444"
            if agent_status == "COMPLETED":
                line_color = "#5CC151" # Green line if this step passed
            connector_html = f'<div style="width: 40px; height: 2px; background-color: {line_color}; flex-shrink: 0;"></div>'

        # Minified Node HTML - Larger Size with Image Support
        html_content += f"""<div class="flow-node" style="border-color: {border_color}; background-color: {bg_color}; box-shadow: 0 4px 8px rgba(0,0,0,0.4); z-index: 2;"><div style="margin-bottom: 8px; display: flex; justify-content: center;">{icon_html}</div><div style="font-size: 11px; text-transform: uppercase; color: #BBB; letter-spacing: 1.5px; margin-bottom: 4px;">Step {i+1}</div><div style="font-weight: 600; font-size: 14px; color: #FFF; text-align: center; white-space: nowrap;">{agent['display_name']}</div></div>{connector_html}"""
        
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)

def render_system_health(status_data, failures_count):
    """
    Renders the System Health Header (Bank-Grade Alert Banner).
    """
    risk_avg = 0 
    
    health = "HEALTHY"
    bg_color = "#E6F4EA"
    border_color = "#1E7E34"
    text_color = "#1E7E34"
    icon = "✓"
    
    if failures_count > 0:
        health = "CRITICAL ATTENTION REQUIRED"
        bg_color = "#FCE8E6"
        border_color = "#DB0011"
        text_color = "#DB0011"
        icon = "!"
    elif risk_avg > 50:
        health = "DEGRADED PERFORMANCE"
        bg_color = "#FFF8E1"
        border_color = "#F57F17"
        text_color = "#F57F17"
        icon = "⚠"
        
    # Minified HTML - Modern Alert Banner
    html_health = f"""<div style="background-color: {bg_color}; padding: 15px 20px; border-left: 5px solid {border_color}; border-radius: 12px; margin-bottom: 30px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 15px rgba(0,0,0,0.2);"><div style="display: flex; align-items: center; gap: 15px;"><div style="background: {border_color}; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px;">{icon}</div><div><div style="font-weight: 700; color: {text_color}; font-size: 14px; letter-spacing: 0.5px;">SYSTEM STATUS: {health}</div><div style="font-size: 12px; color: #555;">Pipeline Status: {status_data.get('overall', {}).get('status', 'UNKNOWN')} | Failures detected: {failures_count}</div></div></div><div style="font-size: 12px; color: #777;">Last Updated: {status_data.get('updated_at', '').split('T')[1][:8]}</div></div>"""
    
    st.markdown(html_health, unsafe_allow_html=True)

def render_agent_cards(status_data):
    """
    Renders the grid of Agent Cards using the .hsbc-card CSS class.
    """
    st.markdown("### Operational Agents")
    
    stages_status = status_data.get("stages", {})
    
    # Grid Layout
    cols = st.columns(3)
    
    for i, agent in enumerate(AGENTS):
        with cols[i % 3]:
            # Status Logic
            agent_status = "PENDING"
            progress = 0
            for stage in agent["stages"]:
                s_data = stages_status.get(stage, {})
                s = s_data.get("status", "PENDING")
                progress = max(progress, s_data.get("progress", 0))
                if s == "FAILED": agent_status = "FAILED"
                elif s == "IN_PROGRESS": agent_status = "IN_PROGRESS"
                elif s == "COMPLETED" and agent_status != "IN_PROGRESS": agent_status = "COMPLETED"
            
            # Badge Class
            badge_class = "badge-neutral"
            if agent_status == "COMPLETED": badge_class = "badge-success"
            elif agent_status == "IN_PROGRESS": badge_class = "badge-warning"
            elif agent_status == "FAILED": badge_class = "badge-error"
            
            # Icon Rendering
            icon_val = agent.get('icon', '🤖')
            icon_html = "🤖"

            if icon_val.endswith('.png'):
                try:
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    rel_path = icon_val.replace("ui/", "") if icon_val.startswith("ui/") else icon_val
                    abs_path = os.path.join(current_dir, rel_path)
                    
                    path_to_open = abs_path if os.path.exists(abs_path) else icon_val
                    
                    with open(path_to_open, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                    icon_html = f'<img src="data:image/png;base64,{encoded_string}" style="width: 80px; height: 80px; object-fit: contain;">'
                except:
                    icon_html = "🤖"
            else:
                 icon_html = f'<div style="font-size: 24px;">{icon_val}</div>'

            # Splunk Card with Cyan Progress Bar
            html_card = f"""<div class="hsbc-card"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">{icon_html}<span class="hsbc-badge {badge_class}">{agent_status}</span></div><div style="font-weight: 500; font-size: 15px; margin-bottom: 5px;">{agent['display_name']}</div><div style="font-size: 11px; color: #BBB; margin-bottom: 15px; height: 35px; overflow: hidden; line-height: 1.4;">{agent['short_desc']}</div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {progress}%;"></div></div><div style="text-align: right; font-size: 10px; color: #888; margin-top: 5px;">Progress: {progress}%</div></div>"""
            
            st.markdown(html_card, unsafe_allow_html=True)

def render_scorecards(metrics):
    """
    Renders large KPI cards using custom HTML/CSS for strict layout control.
    """
    st.markdown("### Portfolio Performance")
    
    kpis = [
        {"label": "Code Quality", "value": f"{metrics.get('quality', 0):.1f}", "delta": "1.2%", "d_type": "pos"},
        {"label": "Cloud Readiness", "value": f"{metrics.get('cloud', 0):.1f}", "delta": "0.5%", "d_type": "pos"},
        {"label": "Risk Score", "value": f"{metrics.get('risk', 0):.0f}", "delta": "-5", "d_type": "pos"}, # Lower risk is pos
        {"label": "Security Health", "value": f"{metrics.get('security', 0):.1f}", "delta": "-1.1%", "d_type": "neg"},
        {"label": "Testing Maturity", "value": metrics.get('testing', 'N/A'), "delta": None, "d_type": "neu"},
        {"label": "Open Findings", "value": metrics.get('findings', 0), "delta": "+2", "d_type": "neg"}
    ]
    
    cols = st.columns(6)
    
    for i, kpi in enumerate(kpis):
        with cols[i]:
            delta_html = ""
            if kpi['delta']:
                c_class = f"delta-{kpi['d_type']}"
                delta_html = f"<span class='hsbc-metric-delta {c_class}'>{kpi['delta']}</span>"
            
            # Minified HTML
            html_kpi = f"""<div class="hsbc-card" style="padding: 1rem; text-align: center;"><div class="hsbc-metric-label">{kpi['label']}</div><div class="hsbc-metric-value">{kpi['value']}</div>{delta_html}</div>"""
            st.markdown(html_kpi, unsafe_allow_html=True)

def render_activity_feed(events, limit=50):
    """
    Renders scrolling activity feed (Log style).
    """
    st.subheader("Live Operations Log")
    with st.container(height=300):
        # We can style this better too
        html = '<div style="font-family: monospace; font-size: 12px;">'
        for event in events[:limit]:
            ts = event['ts'].split("T")[1][:8]
            color = "#333"
            if event['status'] == "FAILED": color = "#DB0011"
            elif event['status'] == "COMPLETED": color = "#1E7E34"
            
            html += f'<div style="border-bottom: 1px solid #EEE; padding: 4px 0;"><span style="color: #999;">[{ts}]</span> <span style="font-weight: bold; color: {color}">{event["stage"]}</span>: {event["message"]}</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
