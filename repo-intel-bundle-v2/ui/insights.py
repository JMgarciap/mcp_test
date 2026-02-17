import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_insights_dashboard(metrics, governance_data):
    """
    Renders the Executive Insights Dashboard.
    """
    st.markdown("## 📊 Executive Insights")
    
    # --- Top Level KPI Cards ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio Health", f"{metrics.get('quality', 0):.1f}/100", delta="1.2%")
    c2.metric("Avg Security Score", f"{metrics.get('security', 0):.1f}/100", delta="-0.5%")
    c3.metric("Critical Risks", metrics.get('risk', 0), delta_color="inverse")
    c4.metric("Avg Velocity", "42 SP", help="Mocked data from Jira")

    st.markdown("---")

    # --- Charts Section ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Distribution")
        # Extract risk levels from governance data
        repos = governance_data.get("repos", [])
        risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        
        for r in repos:
            # Fallback if "risk_level" is missing, deduce from score
            level = r.get("risk_level")
            if not level:
                score = r.get("scores", {}).get("risk", 0)
                if score > 80: level = "Critical"
                elif score > 50: level = "High"
                elif score > 20: level = "Medium"
                else: level = "Low"
            
            if level in risk_counts:
                risk_counts[level] += 1
            else:
                risk_counts["Low"] += 1 # Safety net

        # HSBC / Corporate Palette
        colors = {
            "Critical": "#DB0011",  # HSBC Red
            "High": "#595959",      # Dark Gray (Serious)
            "Medium": "#8C8C8C",    # Mid Gray
            "Low": "#D9D9D9"        # Light Gray
        }
        
        df_risk = pd.DataFrame(list(risk_counts.items()), columns=["Level", "Count"])
        
        fig_risk = px.pie(
            df_risk, 
            values="Count", 
            names="Level", 
            hole=0.6,
            color="Level",
            color_discrete_map=colors
        )
        fig_risk.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial, sans-serif", size=12, color="#333")
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    with col2:
        st.subheader("Compliance Radar")
        # Radar chart comparing Quality, Security, Cloud, Testing
        categories = ['Quality', 'Security', 'Cloud', 'Testing']
        
        # Normalize Testing (Low/Med/High -> 33/66/100)
        test_score = 0
        test_maturity = metrics.get('testing', 'N/A')
        if test_maturity == 'High': test_score = 100
        elif test_maturity == 'Medium': test_score = 66
        elif test_maturity == 'Low': test_score = 33
        
        values = [
            metrics.get('quality', 0),
            metrics.get('security', 0),
            metrics.get('cloud', 0),
            test_score
        ]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=[values[0], values[1], values[2], values[3], values[0]], # Close loop
            theta=['Quality', 'Security', 'Cloud', 'Testing', 'Quality'],
            fill='toself',
            name='Portfolio Avg',
            line_color='#DB0011', # HSBC Red
            fillcolor='rgba(219, 0, 17, 0.2)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor="#ddd"),
                angularaxis=dict(tickfont=dict(size=10, color="#555"))
            ),
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial, sans-serif")
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- Strategic Insights ---
    st.subheader("💡 Strategic Recommendations")
    
    c_strat, c_wins = st.columns([2, 1])
    
    with c_strat:
        # Top Priorities Logic
        st.markdown("**🚨 Top 3 Critical Priorities**")
        
        priorities = []
        for r in repos:
            if r.get("scores", {}).get("risk", 0) > 70:
                priorities.append(f"**{r['name']}**: Critical Risk Detected (Score: {r['scores']['risk']})")
            if r.get("security_score", 100) < 60:
                priorities.append(f"**{r['name']}**: Security posture critical (<60)")
                
        if not priorities:
            st.success("No critical priorities detected. Keep maintaining!")
        else:
            for i, p in enumerate(priorities[:3]):
                st.warning(f"{i+1}. {p}")
                
    with c_wins:
        st.markdown("**⚡ Quick Wins**")
        st.info("• Enable Dependabot on 3 repos")
        st.info("• Archive 2 inactive repos")
        st.info("• Upgrade Python 3.9 -> 3.12")
