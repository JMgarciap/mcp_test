import graphviz
from ui.agent_registry import AGENTS, get_agent_for_stage

def render_pipeline_graph(status_data):
    """
    Render a read-only graph of the pipeline status with icons.
    """
    dot = graphviz.Digraph(comment='Pipeline Flow')
    dot.attr(rankdir='LR') # Left to Right
    dot.attr(bgcolor='transparent')
    
    stages_status = status_data.get("stages", {})
    
    # Nodes from Registry
    for agent in AGENTS:
        if agent.get("future"): continue
        
        # Aggregate status
        agent_status = "PENDING"
        for stage in agent["stages"]:
            s = stages_status.get(stage, {}).get("status", "PENDING")
            if s == "FAILED": agent_status = "FAILED"
            elif s == "IN_PROGRESS": agent_status = "IN_PROGRESS"
            elif s == "COMPLETED" and agent_status != "IN_PROGRESS": agent_status = "COMPLETED"
        
        color = "white"
        fillcolor = "white"
        fontcolor = "black"
        style = "filled"
        
        status_icon = "⚪"
        if agent_status == "COMPLETED":
            fillcolor = "#e6fffa" # Light Green
            color = "#38b2ac"
            status_icon = "✅"
        elif agent_status == "IN_PROGRESS":
            fillcolor = "#ebf8ff" # Light Blue
            color = "#3182ce"
            status_icon = "🟡"
        elif agent_status == "FAILED":
            fillcolor = "#fff5f5" # Light Red
            color = "#e53e3e"
            status_icon = "❌"
            
        label = f"{agent['icon']} {agent['display_name']}\n{status_icon} {agent_status}"
        dot.node(agent['id'], label, shape="box", style=style, fillcolor=fillcolor, color=color, fontname="Arial")

    # Edges ( Sequential Flow )
    active_ids = [a['id'] for a in AGENTS if not a.get("future")]
    for i in range(len(active_ids) - 1):
        dot.edge(active_ids[i], active_ids[i+1])
        
    # Legend
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(label='Legend')
        c.node('l1', 'Completed', fillcolor='#e6fffa', style='filled')
        c.node('l2', 'In Progress', fillcolor='#ebf8ff', style='filled')
        c.node('l3', 'Failed', fillcolor='#fff5f5', style='filled')
        c.attr(rank='same')
    
    return dot
