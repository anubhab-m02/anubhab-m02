import svgwrite
import random

# --- CORE BLUEPRINT ---
OUTPUT_FILENAME = "cognitive_engine.svg"
CANVAS_SIZE = ("1000px", "800px")
BG_COLOR = "#0D1117" # GitHub Dark BG

# Define the modules of the engine
ENGINE_MODULES = {
    "gen_ai_core": {
        "label": "GenAI Core", "pos": (250, 250), "color": "#00FFFF",
        "tech": ["LangGraph", "AutoGen", "FastAPI", "LLM Fine-Tuning"]
    },
    "data_pipeline": {
        "label": "Data Pipeline", "pos": (750, 250), "color": "#FF00FF",
        "tech": ["Apache Kafka", "PySpark", "Databricks", "Oracle DI"]
    },
    "interface_layer": {
        "label": "Interface Layer", "pos": (250, 550), "color": "#00FF00",
        "tech": ["Angular", "React", "State Management", "WebSockets"]
    },
    "service_fabric": {
        "label": "Service Fabric", "pos": (750, 550), "color": "#FFFF00",
        "tech": ["Java", "SpringBoot", "Microservices", "Docker"]
    },
}
CENTRAL_REACTOR_POS = (500, 400)

def generate_engine():
    """Constructs the entire cognitive engine SVG."""
    dwg = svgwrite.Drawing(OUTPUT_FILENAME, size=CANVAS_SIZE, profile='full')
    dwg.add(dwg.rect(insert=(0, 0), size=CANVAS_SIZE, fill=BG_COLOR))

    # --- STYLES & FILTERS (The Soul of the Machine) ---
    dwg.defs.add(dwg.style("""
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        .module-label, .tech-label, .central-label { font-family: 'Roboto Mono', monospace; font-weight: bold; text-anchor: middle; fill: #C9D1D9; }
        .central-label { font-size: 24px; }
        .module-label { font-size: 16px; }
        .tech-label { font-size: 12px; fill: #8B949E; text-anchor: start; opacity: 0; transition: opacity 0.5s ease-in-out; }
        .engine-module:hover .tech-label { opacity: 1; }
        .engine-module:hover .module-ring { stroke-width: 4; }
        
        /* --- Animation Keyframes --- */
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes rotate-reverse { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
        @keyframes pulse { 0%, 100% { stroke-opacity: 0.7; } 50% { stroke-opacity: 1; } }
        @keyframes data-flow { 0% { stroke-dashoffset: 20; } 100% { stroke-dashoffset: 0; } }
    """))
    
    # Glow filter for a neon effect
    glow_filter = dwg.defs.add(dwg.filter(id="glow"))
    glow_filter.feGaussianBlur(stdDeviation="3", result="coloredBlur")
    # Correctly construct the feMerge element
    fe_merge = dwg.feMerge()
    fe_merge.add(dwg.feMergeNode(in_='coloredBlur'))
    fe_merge.add(dwg.feMergeNode(in_='SourceGraphic'))
    glow_filter.add(fe_merge)

    # --- BACKGROUND GRID (The Substrate) ---
    grid_pattern = dwg.defs.add(dwg.pattern(id="grid", width="20", height="20", patternUnits="userSpaceOnUse"))
    grid_pattern.add(dwg.path(d="M 20 0 L 0 0 0 20", fill="none", stroke="#161b22", stroke_width="0.5"))
    dwg.add(dwg.rect(insert=(0, 0), size=CANVAS_SIZE, fill="url(#grid)"))

    # --- CENTRAL REACTOR (The Heart) ---
    reactor_group = dwg.g(id="central-reactor", transform=f"translate({CENTRAL_REACTOR_POS[0]}, {CENTRAL_REACTOR_POS[1]})", filter="url(#glow)")
    # Gyroscopic Rings
    for i, r in enumerate([60, 70, 80]):
        anim_duration = 10 + i * 5
        direction = "rotate" if i % 2 == 0 else "rotate-reverse"
        ring = dwg.circle(center=(0, 0), r=r, stroke="#00FFFF", fill="none", stroke_width=1.5, stroke_opacity=0.8,
                          style=f"transform-box: fill-box; transform-origin: center; animation: {direction} {anim_duration}s linear infinite;")
        reactor_group.add(ring)
    # Pulsing Core
    core = dwg.circle(center=(0, 0), r=45, fill=BG_COLOR, stroke="#FFFFFF", stroke_width=3)
    core.add(dwg.animate('stroke-width', dur="3s", values="3;5;3", repeatCount="indefinite"))
    reactor_group.add(core)
    dwg.add(reactor_group)
    dwg.add(dwg.text("ANUBHAB", insert=CENTRAL_REACTOR_POS, dy="8", class_="central-label"))


    # --- ENGINE MODULES & CONDUITS (The Limbs) ---
    for key, module in ENGINE_MODULES.items():
        m_pos = module["pos"]
        
        # Data Conduits
        conduit = dwg.path(d=f"M {CENTRAL_REACTOR_POS[0]} {CENTRAL_REACTOR_POS[1]} C {CENTRAL_REACTOR_POS[0]} {m_pos[1]}, {m_pos[0]} {CENTRAL_REACTOR_POS[1]}, {m_pos[0]} {m_pos[1]}",
                             stroke=module["color"], stroke_width="1", fill="none", stroke_dasharray="10 10", stroke_opacity="0.6")
        conduit.add(dwg.animate('stroke-dashoffset', dur=f"{random.uniform(2,4)}s", values="20;0", repeatCount="indefinite"))
        dwg.add(conduit)

        # Module Group
        module_group = dwg.g(id=key, class_="engine-module", transform=f"translate({m_pos[0]}, {m_pos[1]})")

        # Pulsing Outer Ring
        ring = dwg.circle(center=(0,0), r=50, stroke=module["color"], fill=BG_COLOR, stroke_width=2, class_="module-ring", filter="url(#glow)")
        ring.add(dwg.animate('stroke-opacity', dur="2s", values="0.7;1;0.7", repeatCount="indefinite", begin=f"{random.uniform(0,2)}s"))
        module_group.add(ring)

        # Internal Gears/Animations
        for i in range(3):
            gear = dwg.circle(center=(0,0), r=15 + i*10, fill="none", stroke=module["color"], stroke_width=0.5, stroke_opacity=0.3)
            gear.add(dwg.animateTransform('rotate', type='rotate', from_=f'0 0 0', to=f'360 0 0', dur=f"{8 + i*4}s", repeatCount="indefinite"))
            module_group.add(gear)

        # Labels
        module_group.add(dwg.text(module["label"], insert=(0, 0), dy="5", class_="module-label"))
        
        # Tech Diagnostic Panel (hidden by default)
        for i, tech in enumerate(module["tech"]):
            module_group.add(dwg.text(f"• {tech}", insert=(60, -15 + i*15), class_="tech-label"))

        dwg.add(module_group)

    dwg.save()
    print(f"Cognitive Engine forged and saved to {OUTPUT_FILENAME}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    generate_engine()

