# Repository Guidelines

## Project Structure & Module Organization
- The app focuses on simulating and visualizing randomized algorithms.
- `app/` is the Flask application root.
- `app/modules/` contains experiment modules; each module uses `simulation.py`, `controller.py`, and `visualization.py` to separate logic, request handling, and Plotly output.
- `app/presentation/templates/` holds Jinja templates for each module page.
- `app/static/` stores shared CSS and static assets.
- `docs/` includes design notes and module write-ups (see `docs/modules/`).

## Build, Test, and Development Commands
- `python3 -m venv venv` / `source venv/bin/activate`: create and activate a virtual environment.
- `pip install -r requirements.txt`: install runtime dependencies.
- `flask --app app run --debug`: run the development server locally.
- `docker build -t randomized-lab .`: build a container image.
- `docker run -p 8000:8000 randomized-lab`: run the containerized app.

## Coding Style & Naming Conventions
- Use 4-space indentation and follow existing module patterns.
- Keep modules in `snake_case` (e.g., `markov_random_walks`).
- Use descriptive function names that reflect the simulation step (`simulate_*`, `build_*`, `prepare_*`).
- No formatter or linter is configured; keep changes consistent with nearby files.

## Testing Guidelines
- There is no automated test suite yet.
- When adding tests, prefer unit tests for `simulation.py` functions and keep them independent of the Flask layer.
- Recommended naming: `test_<module>_<behavior>.py` in a future `tests/` directory.

## Commit & Pull Request Guidelines
- Recent commit history uses short, lowercase, imperative summaries (e.g., `added bloom filter simulation`).
- Keep commits focused on one module or feature.
- For pull requests, include a summary, any module screenshots/GIFs if the UI changes, and link related issues if available.

## Configuration & Security Notes
- Flask uses a development `SECRET_KEY` in `app/__init__.py`; set a secure value for production.
- Avoid adding secrets to tracked files; use environment variables or deployment settings instead.
