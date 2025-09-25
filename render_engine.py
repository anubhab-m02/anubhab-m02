import svgwrite
import requests
import math
import random
import sys
from datetime import datetime, timedelta

# --- CONFIGURATION ---
GITHUB_TOKEN = sys.argv[1]
USERNAME = sys.argv[2]
OUTPUT_FILENAME = "neural_canvas.svg"

COMPETENCY_HUBS = {
    "gen_ai_agents": {
        "label": "GenAI & Agents", "pos": (250, 250), "keywords": ["langchain", "autogen", "llm", "agent", "fastapi", "genai"], "color": "#00FFFF"
    },
    "data_engineering": {
        "label": "Data Engineering", "pos": (750, 250), "keywords": ["spark", "kafka", "databricks", "etl", "pipeline", "oracle"], "color": "#FF00FF"
    },
    "frontend_dev": {
        "label": "Frontend", "pos": (250, 550), "keywords": ["angular", "react", "frontend", "ui", "css", "typescript"], "color": "#00FF00"
    },
    "backend_services": {
        "label": "Backend", "pos": (750, 550), "keywords": ["java", "springboot", "microservice", "backend", "api", "server"], "color": "#FFFF00"
    },
}
CENTRAL_NODE_POS = (500, 400)
CANVAS_SIZE = ("1000px", "800px")
BG_COLOR = "#000005" # Deep space blue/black

# --- GITHUB API FETCHER ---
def get_github_activity(token, username):
    events = []
    headers = {'Authorization': f'token {token}'}
    url = f"https://api.github.com/users/{username}/events/public?per_page=100"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        all_events = response.json()
        
        # Look for push events in the last year for a richer history
        since = datetime.utcnow() - timedelta(days=365)
        for event in all_events:
            if event['type'] == 'PushEvent' and datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ") > since:
                if 'commits' in event['payload'] and event['payload']['commits']:
                    events.append({
                        "repo": event['repo']['name'],
                        "timestamp": datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ"),
                        "commits": event['payload']['commits'],
                        "url": f"https://github.com/{event['repo']['name']}/commit/{event['payload']['head']}" if event['payload'].get('head') else f"https://github.com/{event['repo']['name']}"
                    })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub activity: {e}")
    return events

# --- SVG GENERATION ENGINE ---
def create_starfield(dwg, number_of_stars):
    """Generates a random starfield background."""
    for _ in range(number_of_stars):
        x, y = random.randint(0, 1000), random.randint(0, 800)
        r = random.uniform(0.2, 1.2)
        opacity = random.uniform(0.3, 1.0)
        star = dwg.circle(center=(f"{x}px", f"{y}px"), r=f"{r}px", fill="white", opacity=opacity)
        star.add(dwg.animate('opacity', dur=f"{random.uniform(2, 6)}s", values=f"{opacity};{opacity*0.5};{opacity}", repeatCount="indefinite"))
        dwg.add(star)

def render_base_canvas(dwg):
    """Renders the foundational elements of the canvas: background, stars, hubs."""
    dwg.defs.add(dwg.style("""
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        .hub-label, .central-label, .status-text { font-family: 'Roboto Mono', monospace; font-weight: bold; text-anchor: middle; }
        .hub-label { font-size: 14px; fill: #AAAAAA; }
        .central-label { font-size: 18px; fill: #FFFFFF; }
        .status-text { font-size: 16px; fill: #555; font-style: italic; }
        .connection-line { stroke: #FFFFFF; stroke-width: 0.5; stroke-opacity: 0.1; }
        .activity-node { transition: all 0.3s ease; cursor: pointer; }
        .activity-node:hover { stroke-width: 4; stroke-opacity: 1; }
        @keyframes centralPulse { 0% { stroke-opacity: 0.5; } 50% { stroke-opacity: 1; } 100% { stroke-opacity: 0.5; } }
        @keyframes hubPulse { 0% { stroke-opacity: 0.3; } 50% { stroke-opacity: 0.8; } 100% { stroke-opacity: 0.3; } }
        @keyframes echoPulse { 0%, 100% { opacity: 0; } 50% { opacity: 0.4; } }
        @keyframes cometEnter { from { opacity: 0; } to { opacity: 1; } }
    """))
    
    # Add filters for glow effects
    glow_filter = dwg.defs.add(dwg.filter(id="glow"))
    glow_filter.feGaussianBlur(stdDeviation="3.5", result="coloredBlur")
    feMerge = glow_filter.feMerge()
    feMerge.feMergeNode(in_="coloredBlur")
    feMerge.feMergeNode(in_="SourceGraphic")

    # Draw background and starfield
    dwg.add(dwg.rect(insert=(0, 0), size=CANVAS_SIZE, fill=BG_COLOR))
    create_starfield(dwg, 200)

    # Draw central node (The Star)
    center_group = dwg.g(filter="url(#glow)")
    center_circle = dwg.circle(center=CENTRAL_NODE_POS, r=45, stroke="#FFFFFF", fill=BG_COLOR, stroke_width=2)
    center_circle.add(dwg.animate('stroke-opacity', dur="4s", values="0.5;1;0.5", repeatCount="indefinite"))
    center_group.add(center_circle)
    dwg.add(center_group)
    dwg.add(dwg.text("ANUBHAB", insert=(CENTRAL_NODE_POS[0], CENTRAL_NODE_POS[1] + 6), class_="central-label"))

    # Draw competency hubs (The Nebulae)
    for key, hub in COMPETENCY_HUBS.items():
        dwg.add(dwg.line(start=CENTRAL_NODE_POS, end=hub["pos"], class_="connection-line"))
        hub_group = dwg.g(filter="url(#glow)")
        hub_circle = dwg.circle(center=hub["pos"], r=35, stroke=hub["color"], fill=BG_COLOR, stroke_width=2)
        hub_circle.add(dwg.animate('stroke-opacity', dur=f"{random.uniform(3, 6)}s", values="0.3;0.8;0.3", repeatCount="indefinite"))
        hub_group.add(hub_circle)
        dwg.add(hub_group)
        dwg.add(dwg.text(hub["label"], insert=(hub["pos"][0], hub["pos"][1] + 55), class_="hub-label"))
    return dwg

def render_active_canvas(activity):
    """Renders the canvas with live activity nodes (Comets)."""
    dwg = svgwrite.Drawing(OUTPUT_FILENAME, size=CANVAS_SIZE, profile='full')
    dwg = render_base_canvas(dwg)
    
    now = datetime.utcnow()
    recent_threshold = now - timedelta(days=14)

    for event in reversed(activity[:30]): # Render up to 30 nodes
        if event["timestamp"] < recent_threshold: continue

        hub_key = next((key for key, hub in COMPETENCY_HUBS.items() if any(k in event["repo"].lower() for k in hub["keywords"])), None)
        if not hub_key: continue

        hub_pos = COMPETENCY_HUBS[hub_key]["pos"]
        angle = random.uniform(0, 2 * math.pi)
        
        age_delta = (now - event["timestamp"]).total_seconds()
        age_factor = 1 - min(age_delta / (14 * 24 * 3600), 1)
        distance = 50 + (60 * age_factor * random.uniform(0.9, 1.1))
        
        node_pos = (hub_pos[0] + distance * math.cos(angle), hub_pos[1] + distance * math.sin(angle))
        radius = 3 + (4 * age_factor)
        
        link = dwg.add(dwg.a(href=event["url"], target="_blank"))
        commit_message = event["commits"][0]['message'].split('\n')[0][:40]
        link.add(dwg.title(f"{event['repo']}\n{commit_message}..."))
        
        comet = dwg.circle(
            center=node_pos, r=radius, fill="none",
            stroke=COMPETENCY_HUBS[hub_key]["color"], stroke_width=2,
            stroke_opacity=0.4 + (0.6 * age_factor), class_="activity-node"
        )
        comet.add(dwg.animate('opacity', dur="1s", values="0;1", repeatCount="1"))
        link.add(comet)

    dwg.save()
    print(f"Active Constellation rendered to {OUTPUT_FILENAME}")

def render_dormant_canvas(activity):
    """Renders the canvas in its 'remembering' state with echoes of past work."""
    dwg = svgwrite.Drawing(OUTPUT_FILENAME, size=CANVAS_SIZE, profile='full')
    dwg = render_base_canvas(dwg)

    # Use older, significant commits as echoes
    for event in random.sample(activity, min(len(activity), 15)):
        hub_key = next((key for key, hub in COMPETENCY_HUBS.items() if any(k in event["repo"].lower() for k in hub["keywords"])), None)
        if not hub_key: continue

        hub_pos = COMPETENCY_HUBS[hub_key]["pos"]
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, 110)
        node_pos = (hub_pos[0] + distance * math.cos(angle), hub_pos[1] + distance * math.sin(angle))
        
        echo = dwg.circle(center=node_pos, r=random.uniform(3, 6), fill=COMPETENCY_HUBS[hub_key]["color"], opacity=0)
        echo.add(dwg.animate('opacity', dur=f"{random.uniform(4, 8)}s", values="0;0.4;0", repeatCount="indefinite", begin=f"{random.uniform(0, 4)}s"))
        dwg.add(echo)

    dwg.add(dwg.text("Remembering past signals...", insert=(CENTRAL_NODE_POS[0], CANVAS_SIZE[1].replace('px','') - 50), class_="status-text"))
    dwg.save()
    print(f"Dormant Constellation (Echoes) rendered to {OUTPUT_FILENAME}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    all_activity = get_github_activity(GITHUB_TOKEN, USERNAME)
    recent_activity = [e for e in all_activity if e['timestamp'] > datetime.utcnow() - timedelta(days=14)]

    if recent_activity:
        print(f"Found {len(recent_activity)} recent events. Rendering Active Constellation.")
        render_active_canvas(recent_activity)
    elif all_activity:
        print("No recent activity. Rendering Dormant Constellation with historical echoes.")
        render_dormant_canvas(all_activity)
    else:
        print("No activity found at all. Rendering base dormant canvas.")
        # This will create a basic dormant canvas if API fails or there's zero history
        render_dormant_canvas([])

