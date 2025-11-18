# Randomized Experiments Lab — Design Document

## Vision
- Build a modular Flask-based playground that demonstrates the behavior of randomized algorithms through curated experiments.
- Keep everything server-rendered to avoid heavy frontend stacks while still delivering interactive experiences through Plotly.
- Each experiment lives in its own module so adding future experiments does not disturb existing ones.

## Technology Choices
- **Backend framework:** Flask for simple routing, templating, and modular blueprints.
- **Templating / presentation:** Jinja templates + Bootstrap utility classes for a lightweight, responsive layout.
- **Graph + statistics engine:** NetworkX for generating Erdős–Rényi graphs and computing structural properties.
- **Visualization:** Plotly (rendered to HTML/JSON) for node-link diagrams and animated playback; embedded directly into Jinja templates.
- **State storage:** No database; parameters are passed per request (query/form). Playback sequences generated on demand.

## High-Level Architecture
```
/app_randomized_simulations
  /presentation
    __init__.py          # Flask app factory, registers blueprints
    routes.py            # Home + module routes
    templates/           # Shared layout, module pages
    static/              # CSS overrides, Plotly bundle (if needed)
  /modules
    __init__.py
    phase_transition/
      controller.py      # Handles request params, orchestrates runs
      simulation.py      # Pure logic for generating graphs & stats
      visualization.py   # Plotly figure builders
```

### Layer Responsibilities
- **Presentation layer**
  - Exposes Flask routes for home and modules.
  - Validates user input and invokes module controllers.
  - Renders templates, embedding Plotly figure JSON or HTML.
- **Application layer (experiments/modules)**
  - Provides a consistent interface: `generate(params) -> {frames, stats, metadata}`.
  - Houses algorithmic logic (graph generation, statistics, phase threshold calculations).
  - Keeps pure functions where possible for easy testing.

### Data Flow
1. User chooses module from the landing page and submits parameters (e.g., number of vertices, p increment, playback speed).
2. Module controller parses parameters and requests sample graphs from `simulation.py`.
3. Simulation returns a sequence of states: each state contains `p`, underlying NetworkX graph, computed stats.
4. Visualization builder converts the sequence into Plotly frames (nodes, edges, highlight largest component, etc.).
5. Presentation layer renders the module template with:
   - Plotly JSON/HTML block for playback.
   - Tabular statistics for each `p`.
   - Phase transition thresholds drawn on the probability axis.

## Module: Random Graph Phase Transitions

### Goals
- Illustrate how Erdős–Rényi \( G(n, p) \) transitions from disconnected components to a giant component and beyond.
- Provide both visual (graph animation) and numeric cues (statistics + theoretical thresholds).

### Parameters (pre-run form)
- `n_vertices` (default 75): number of nodes in the graph.
- `p_start`, `p_end`, `p_step` (defaults 0.0 → 1.0, 0.02 step): probability sweep range.
- `playback_speed` (ms per frame) to control Plotly animation interval.
- `seed` (optional) for reproducibility.

### Computed Statistics per state
- Largest component size.
- Number of components.
- Is graph connected?
- Number of edges.
- Presence of cycle (detected via `cycle_basis`).
- Presence of triangle & count of triangles (via `nx.triangles` sum / 3).
- Average degree.
- Clustering coefficient (global).

### Theoretical Phase Markers
- `p = 1/n`: first cycle likely.
- `p = log(n)/n`: connectivity threshold.
- `p = 1/(√n)`: plentitude of triangles (informal marker).
- `p = 0.5`: dense regime indicator.
- Markers displayed as vertical lines on the probability axis alongside textual explanation.

### Visualization
- Force-directed layout computed once per `n` to minimize jitter; reuse node positions across frames.
- Nodes colored by component: largest component highlighted, others muted.
- Optional tooltips: node degree, component ID.
- Plotly animation controls: play/pause, slider tied to `p`.
- Stats panel updates with current frame values; include a table listing `p` vs stats for quick scanning.

## Presentation Layer UI

### Landing Page
- Top navigation bar with app name and dropdown for modules.
- Hero card introducing the lab, with quick description and “Get Started” button linking to the default experiment.
- Grid of cards, one per module, showing title, synopsis, and “Launch” button (future modules can link to placeholder pages).

### Module Page Layout (Phase Transition)
- Two-column layout:
  - **Left column (~30%)**: parameter form at top (collapsible), stats panel below with live values and theoretical markers legend.
  - **Right column (~70%)**: Plotly visualization container with animation controls and timeline indicator.
- After form submission, render results beneath the form without reloading entire page (simple POST-redirect-GET pattern).
- Provide a “Reset parameters” button to return to defaults quickly.

### Styling Notes
- Use Bootstrap for responsive grid, cards, buttons.
- Custom SCSS/CSS for module-specific highlights (e.g., color palette for components).
- Minimal JS: rely on Plotly’s embedded bundle; no custom browser-side logic beyond what Plotly injects.

## Extensibility Considerations
- Every module registers metadata: `slug`, `name`, `description`, `controller`.
- Home page iterates over registered modules to render cards automatically.
- Shared utilities (e.g., RNG helpers, caching layout positions) live in `modules/common`.
- Future experiments can focus on other randomized algorithms (Monte Carlo integration, randomized sorting, percolation) by adding new subpackages under `/modules`.

## Module Guides
Each experiment has a dedicated guide detailing parameters, outputs, and future ideas:

- [Phase Transition (G(n, p))](modules/phase_transition.md)
- [Edge Process (G(n, m))](modules/g_nm.md)
- [Monte Carlo Union of Rectangles](modules/union_area.md)

## Delivery Plan
1. Scaffold Flask project structure with presentation + modules directories.
2. Implement module registry + landing page.
3. Build phase transition module (simulation, visualization, controller, template).
4. Style landing/module pages with Bootstrap + custom CSS.
5. Add tests for simulation logic (component counts, threshold calculations) to ensure correctness without a browser.
