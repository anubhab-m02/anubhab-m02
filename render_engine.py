import svgwrite
import requests
import math
import random
import sys
from collections import defaultdict
from datetime import datetime, timedelta

# --- CONFIGURATION ---
GITHUB_TOKEN = sys.argv[1]
USERNAME = sys.argv[2]
OUTPUT_FILENAME = "neural_canvas.svg"

# Define core competency hubs and their associated keywords/repos
# This mapping determines where activity nodes spawn.
COMPETENCY_HUBS = {
    "gen_ai_agents": {
        "label": "GenAI & Agents",
        "pos": (200, 200),
        "keywords": ["langchain", "autogen", "llm", "agent", "fastapi", "genai"],
        "color": "#00FFFF" # Cyan
    },
    "data_engineering": {
        "label": "Data Engineering",
        "pos": (800, 200),
        "keywords": ["spark", "kafka", "databricks", "etl", "pipeline", "oracle"],
        "color": "#FF00FF" # Magenta
    },
    "frontend_dev": {
        "label": "Frontend",
        "pos": (200, 600),
        "keywords": ["angular", "react", "frontend", "ui", "css", "typescript"],
        "color": "#00FF00" # Green
    },
    "backend_services": {
        "label": "Backend",
        "pos": (800, 600),
        "keywords": ["java", "springboot", "microservice", "backend", "api", "server"],
        "color": "#FFFF00" # Yellow
    },
}
CENTRAL_NODE_POS = (500, 400)
CANVAS_SIZE = ("1000px", "800px")
BG_COLOR = "#0A0A0A"

# --- GITHUB API FETCHER ---
def get_github_activity(token, username):
    """Fetches recent public push events for the user."""
    events = []
    headers = {'Authorization': f'token {token}'}
    url = f"https://api.github.com/users/{username}/events/public"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        all_events = response.json()
        # Filter for push events in the last 14 days
        since = datetime.utcnow() - timedelta(days=14)
        for event in all_events:
            if event['type'] == 'PushEvent' and datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ") > since:
                events.append({
                    "repo": event['repo']['name'],
                    "timestamp": datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ"),
                    "commits": event['payload']['commits'],
                    "url": f"https://github.com/{event['repo']['name']}/commit/{event['payload']['head']}"
                })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub activity: {e}")
    return events[:20] # Limit to most recent 20 events

# --- SVG GENERATION ENGINE ---
def render_canvas(activity):
    """Generates the SVG neural canvas based on GitHub activity."""
    dwg = svgwrite.Drawing(OUTPUT_FILENAME, size=CANVAS_SIZE, profile='full')

    # Add embedded CSS for animations and styles
    dwg.defs.add(dwg.style("""
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        .hub-label { font-family: 'Roboto Mono', monospace; font-size: 14px; fill: #CCCCCC; font-weight: bold; text-anchor: middle; }
        .central-label { font-family: 'Roboto Mono', monospace; font-size: 18px; fill: #FFFFFF; font-weight: bold; text-anchor: middle; }
        .hub-circle { stroke-width: 2; fill: none; }
        .connection-line { stroke: #333333; stroke-width: 1; stroke-dasharray: 4 4; }
        .activity-node { stroke-width: 1.5; transition: all 0.3s ease; }
        .activity-node:hover { r: 10; stroke-width: 3; }
        @keyframes pulse { 0% { r: 6; opacity: 1; } 50% { r: 12; opacity: 0.5; } 100% { r: 6; opacity: 1; } }
        .recent-node { animation: pulse 2s infinite; }
    """))

    # Draw background
    dwg.add(dwg.rect(insert=(0, 0), size=CANVAS_SIZE, fill=BG_COLOR))

    # Draw central node (You)
    dwg.add(dwg.circle(center=CENTRAL_NODE_POS, r=40, stroke="#FFFFFF", fill=BG_COLOR, stroke_width=2))
    dwg.add(dwg.text("ANUBHAB", insert=(CENTRAL_NODE_POS[0], CENTRAL_NODE_POS[1] + 5), class_="central-label"))

    # Draw competency hubs and connections
    for key, hub in COMPETENCY_HUBS.items():
        dwg.add(dwg.line(start=CENTRAL_NODE_POS, end=hub["pos"], class_="connection-line"))
        dwg.add(dwg.circle(center=hub["pos"], r=30, stroke=hub["color"], class_="hub-circle"))
        dwg.add(dwg.text(hub["label"], insert=(hub["pos"][0], hub["pos"][1] + 45), class_="hub-label"))

    # Draw activity nodes
    now = datetime.utcnow()
    for event in reversed(activity): # Draw oldest first
        hub_key = None
        for key, hub in COMPETENCY_HUBS.items():
            if any(k in event["repo"].lower() for k in hub["keywords"]):
                hub_key = key
                break
        
        if not hub_key: continue # Skip if no matching hub

        hub_pos = COMPETENCY_HUBS[hub_key]["pos"]
        angle = random.uniform(0, 2 * math.pi)
        
        # Newer events are closer to the hub
        age_delta = (now - event["timestamp"]).total_seconds()
        age_factor = 1 - min(age_delta / (14 * 24 * 3600), 1) # Normalize age over 14 days
        distance = 40 + (80 * age_factor * random.uniform(0.8, 1.2)) # Spawn between 40px and 120px
        
        node_pos = (
            hub_pos[0] + distance * math.cos(angle),
            hub_pos[1] + distance * math.sin(angle)
        )
        
        radius = 4 + (4 * age_factor) # Newer nodes are bigger
        opacity = 0.6 + (0.4 * age_factor)
        
        node_class = "activity-node"
        if age_factor > 0.8: # Very recent
             node_class += " recent-node"

        link = dwg.add(dwg.a(href=event["url"], target="_blank"))
        commit_message = event["commits"][0]['message'].split('\n')[0][:40] # First line, truncated
        link.add(dwg.title(f"{event['repo']}\n{commit_message}..."))
        link.add(dwg.circle(
            center=node_pos, 
            r=radius, 
            fill=COMPETENCY_HUBS[hub_key]["color"],
            stroke="#FFFFFF",
            opacity=opacity,
            class_=node_class
        ))

    dwg.save()
    print(f"Neural canvas rendered to {OUTPUT_FILENAME}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    activity_data = get_github_activity(GITHUB_TOKEN, USERNAME)
    if activity_data:
        render_canvas(activity_data)
    else:
        print("No recent activity found to render.")
