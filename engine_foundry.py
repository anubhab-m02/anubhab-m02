import svgwrite
import random
import sys

# --- CORE BLUEPRINT ---
OUTPUT_FILENAME = "cognitive_engine.svg"
CANVAS_SIZE = ("1000px", "800px")
BG_COLOR = "#0D1117" # GitHub Dark BG
REPO_URL = "https://github.com/anubhab-m02/anubhab-m02" # CHANGE THIS IF YOUR REPO URL IS DIFFERENT

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

def generate_engine(focus_module=None):
    """Constructs the entire cognitive engine SVG, with an optional focus state."""
    dwg = svgwrite.Drawing(OUTPUT_FILENAME, size=CANVAS_SIZE, profile='full')
    dwg.add(dwg.rect(insert=(0, 0), size=CANVAS_SIZE, fill=BG_COLOR))

    # --- STYLES & FILTERS (The Soul of the Machine) ---
    dwg.defs.add(dwg.style(f"""
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        .module-label, .tech-label, .central-label, .reset-label {{ font-family: 'Roboto Mono', monospace; font-weight: bold; text-anchor: middle; fill: #C9D1D9; }}
        .central-label {{ font-size: 24px; }}
        .reset-label {{ font-size: 12px; fill: #8B949E; cursor: pointer; }}
        .reset-label:hover {{ fill: #FFFFFF; text-decoration: underline; }}
        .module-label {{ font-size: 16px; }}
        .tech-label {{ font-size: 12px; fill: #8B949E; text-anchor: start; opacity: 0; transition: opacity 0.5s ease-in-out; }}
        .engine-module:hover .tech-label {{ opacity: 1; }}
        .engine-module.focused .tech-label {{ opacity: 1; }}
        .engine-module:hover .module-ring {{ stroke-width: 4; }}
        .engine-module.focused .module-ring {{ stroke-width: 4; }}
        .engine-module.dimmed {{ opacity: 0.4; transition: opacity 0.5s ease-in-out; }}

        /* --- Animation Keyframes --- */
        @keyframes rotate {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
        @keyframes rotate-reverse {{ from {{ transform: rotate(360deg); }} to {{ transform: rotate(0deg); }} }}
        @keyframes pulse {{ 0%, 100% {{ stroke-opacity: 0.7; }} 50% {{ stroke-opacity: 1; }} }}
        @keyframes data-flow {{ 0% {{ stroke-dashoffset: 20; }} 100% {{ stroke-dashoffset: 0; }} }}
    """))
    
    glow_filter = dwg.defs.add(dwg.filter(id="glow"))
    glow_filter.feGaussianBlur(stdDeviation="3", result="coloredBlur")
    glow_filter.feMerge(['coloredBlur', 'SourceGraphic'])

    grid_pattern = dwg.defs.add(dwg.pattern(id="grid", width="20", height="20", patternUnits="userSpaceOnUse"))
    grid_pattern.add(dwg.path(d="M 20 0 L 0 0 0 20", fill="none", stroke="#161b22", stroke_width="0.5"))
    dwg.add(dwg.rect(insert=(0, 0), size=CANVAS_SIZE, fill="url(#grid)"))

    # --- CENTRAL REACTOR (The Heart) ---
    reactor_group = dwg.g(id="central-reactor", transform=f"translate({CENTRAL_REACTOR_POS[0]}, {CENTRAL_REACTOR_POS[1]})", filter="url(#glow)")
    for i, r in enumerate([60, 70, 80]):
        anim_duration = 10 + i * 5
        direction = "rotate" if i % 2 == 0 else "rotate-reverse"
        ring = dwg.circle(center=(0, 0), r=r, stroke="#00FFFF", fill="none", stroke_width=1.5, stroke_opacity=0.8,
                          style=f"transform-box: fill-box; transform-origin: center; animation: {direction} {anim_duration}s linear infinite;")
        reactor_group.add(ring)
    core = dwg.circle(center=(0, 0), r=45, fill=BG_COLOR, stroke="#FFFFFF", stroke_width=3)
    core.add(dwg.animate('stroke-width', dur="3s", values="3;5;3", repeatCount="indefinite"))
    reactor_group.add(core)
    dwg.add(reactor_group)
    dwg.add(dwg.text("ANUBHAB", insert=CENTRAL_REACTOR_POS, dy="8", class_="central-label"))
    # Add a reset link if a module is focused
    if focus_module:
        reset_link = dwg.a(href=f"{REPO_URL}/actions/workflows/build_engine.yml/dispatches?ref=main&inputs[focus]=default", target="_top")
        reset_link.add(dwg.text("[ Reset View ]", insert=(CENTRAL_REACTOR_POS[0], CENTRAL_REACTOR_POS[1] + 35), class_="reset-label"))
        dwg.add(reset_link)


    # --- ENGINE MODULES & CONDUITS (The Limbs) ---
    for key, module in ENGINE_MODULES.items():
        is_focused = (key == focus_module)
        is_dimmed = (focus_module is not None and not is_focused)
        
        m_pos = module["pos"]
        
        conduit = dwg.path(d=f"M {CENTRAL_REACTOR_POS[0]} {CENTRAL_REACTOR_POS[1]} C {CENTRAL_REACTOR_POS[0]} {m_pos[1]}, {m_pos[0]} {CENTRAL_REACTOR_POS[1]}, {m_pos[0]} {m_pos[1]}",
                             stroke=module["color"], stroke_width="1", fill="none", stroke_dasharray="10 10", stroke_opacity="0.6")
        conduit.add(dwg.animate('stroke-dashoffset', dur=f"{random.uniform(2,4)}s", values="20;0", repeatCount="indefinite"))
        if is_dimmed:
             conduit['class'] = 'dimmed'
        dwg.add(conduit)

        module_class = "engine-module"
        if is_focused:
            module_class += " focused"
        elif is_dimmed:
            module_class += " dimmed"

        # Create a hyperlink for the entire module to trigger the action
        link = dwg.a(href=f"{REPO_URL}/actions/workflows/build_engine.yml/dispatches?ref=main&inputs[focus]={key}", target="_top")
        module_group = dwg.g(id=key, class_=module_class, transform=f"translate({m_pos[0]}, {m_pos[1]})")

        ring = dwg.circle(center=(0,0), r=50, stroke=module["color"], fill=BG_COLOR, stroke_width=2, class_="module-ring", filter="url(#glow)")
        ring.add(dwg.animate('stroke-opacity', dur="2s", values="0.7;1;0.7", repeatCount="indefinite", begin=f"{random.uniform(0,2)}s"))
        module_group.add(ring)

        for i in range(3):
            gear = dwg.circle(center=(0,0), r=15 + i*10, fill="none", stroke=module["color"], stroke_width=0.5, stroke_opacity=0.3)
            gear.add(dwg.animateTransform('rotate', type='rotate', from_='0 0 0', to='360 0 0', dur=f"{8 + i*4}s", repeatCount="indefinite"))
            module_group.add(gear)

        module_group.add(dwg.text(module["label"], insert=(0, 0), dy="5", class_="module-label"))
        
        for i, tech in enumerate(module["tech"]):
            module_group.add(dwg.text(f"• {tech}", insert=(60, -15 + i*15), class_="tech-label"))
        
        link.add(module_group)
        dwg.add(link)

    dwg.save()
    print(f"Cognitive Engine forged with focus on '{focus_module or 'default'}' and saved to {OUTPUT_FILENAME}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Read the focus module from command-line arguments
    focus = sys.argv[1] if len(sys.argv) > 1 else None
    if focus == 'default':
        focus = None
    generate_engine(focus_module=focus)
```

### Activation Protocol Update

Your `engine_foundry.py` is ready. Now, you must update your GitHub Action to pass commands to it.

**Update your `.github/workflows/build_engine.yml` file to this:**

```yaml
name: Build Cognitive Engine

on:
  push:
    paths:
      - 'engine_foundry.py'
  workflow_dispatch:
    inputs:
      focus:
        description: 'The engine module to focus on (e.g., gen_ai_core or default)'
        required: true
        default: 'default'

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install svgwrite

      - name: Forge the Engine
        run: python ./engine_foundry.py ${{ github.event.inputs.focus }}

      - name: Commit and push the Engine
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add cognitive_engine.svg
          if ! git diff --staged --quiet; then
            git commit -m "refactor(engine): set focus to ${{ github.event.inputs.focus }}"
            git push
          else
            echo "Engine state is already current."
          fi

