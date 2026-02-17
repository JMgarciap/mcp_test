import streamlit as st

def load_css():
    """
    Injects the HSBC Enterprise CSS Design System into the Streamlit app.
    """
    st.markdown("""
<style>
    /* -----------------------------------------------------------------------
       SPLUNK-INSPIRED DARK THEME
       Palette: Deep Blue #0B1116 | Cyan #00A3E0 | Orange #F58220 | Charcoal #212529
       Style: High contrast, data-heavy, dashboard aesthetic.
    ----------------------------------------------------------------------- */

    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    :root {
        --bg-dark: #0B1116;  /* Deep Splunk Blue/Black */
        --card-bg: #171D22;  /* Slightly lighter card background */
        --text-primary: #FFFFFF;
        --text-secondary: #C3C3C3;
        --accent-cyan: #00A3E0;  /* Splunk Blue/Cyan */
        --accent-orange: #F58220; /* Splunk Orange */
        --success-green: #5CC151; /* Splunk Green */
        --error-red: #D93F3C;     /* Splunk Red */
        --border-color: #2D3339;
    }

    /* --- Global Reset --- */
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif !important;
        color: var(--text-primary);
        background-color: var(--bg-dark);
    }
    
    .stApp {
        background-color: var(--bg-dark);
    }

    /* --- Headers --- */
    h1, h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* --- Cards (Splunk Dashboard Panels) --- */
    .hsbc-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 4px; /* Flatter, more technical look */
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: none; /* Flat design */
    }
    
    /* --- Activity Feed --- */
    .activity-feed-container {
        font-family: 'Roboto Mono', monospace;
        font-size: 12px;
        background-color: #0B1116;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 10px;
    }

    /* --- Finding Cards (Results Explorer) --- */
    .finding-card {
        background-color: #212529 !important;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        transition: transform 0.1s;
    }
    .finding-card:hover {
        transform: translateX(2px);
        border-color: #666;
    }
    .finding-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }
    .finding-badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        color: white;
        text-transform: uppercase;
    }
    .finding-title {
        font-weight: 600;
        font-size: 16px;
        color: #FFF;
        margin-bottom: 4px;
    }
    .finding-desc {
        font-size: 13px;
        color: #CCC;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    .finding-remediation {
        background: #2D3339;
        padding: 8px;
        border-radius: 4px;
        font-size: 11px;
        color: #AAA;
        font-family: 'Roboto Mono', monospace;
        border-left: 3px solid #F58220;
    }
    .finding-meta {
        margin-top: 8px;
        font-size: 11px;
        color: #666;
        display: flex;
        gap: 15px;
    }
    .finding-meta span {
        color: #888;
    }
    .finding-meta strong {
        color: #BBB;
    }
    
    /* --- n8n Flow Nodes --- */
    .flow-node {
        background-color: #212529;
        border: 1px solid #444;
        border-radius: 20px;
        padding: 30px 40px; /* Massive padding */
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 260px; /* Wide enough for 120px icons */
        position: relative;
        z-index: 2;
        transition: transform 0.2s;
    }
    
    .flow-node:hover {
        transform: scale(1.05);
        border-color: var(--accent-cyan);
        box-shadow: 0 0 10px rgba(0, 163, 224, 0.3);
    }
    
    .flow-line {
        position: absolute;
        height: 2px;
        background-color: #444;
        top: 50%;
        left: 100%;
        width: 30px; /* Gap between nodes */
        z-index: 1;
    }
    
    /* --- Metrics (Splunk Big Number) --- */
    .hsbc-metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0px;
    }
    
    .hsbc-metric-value {
        font-size: 3rem;
        font-weight: 700;
        color: var(--text-primary); 
    }
    
    .hsbc-metric-delta {
        font-size: 1rem;
        font-weight: 600;
        margin-left: 8px;
    }
    
    .delta-pos { color: var(--success-green); }
    .delta-neg { color: var(--error-red); }
    .delta-neu { color: var(--text-secondary); }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #222;
    }
    
    /* --- Progress Bars --- */
    .progress-bar-bg {
        background-color: #2D3339;
        height: 8px;
        width: 100%;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 4px;
        background-color: var(--accent-cyan); /* Default to Cyan */
    }
    
    /* --- Badges --- */
    .hsbc-badge {
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .badge-success { background-color: rgba(92, 193, 81, 0.2); color: var(--success-green); }
    .badge-warning { background-color: rgba(245, 130, 32, 0.2); color: var(--accent-orange); }
    .badge-error { background-color: rgba(217, 63, 60, 0.2); color: var(--error-red); }
    .badge-neutral { background-color: rgba(255, 255, 255, 0.1); color: var(--text-secondary); }

</style>
    """, unsafe_allow_html=True)
