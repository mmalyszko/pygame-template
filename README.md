# Pygame Template

Python/pygame template for simple games.

## Structure

| Folder      | Purpose                                                             |
|-------------|---------------------------------------------------------------------|
| `src/core/` | Generic, game-agnostic code - can be copied 1:1 into a new project. |
| `src/game/` | Game-specific code - intended to be replaced or extended.           |

Work in progress.

## Demo game

`src/game/` contains a simple raycasting example with player movement, wall collision detection and a minimap.

## Development

Create & activate venv: `python3 -m venv .venv && source .venv/bin/activate`

Install dev tools: `pip install -r requirements-dev.txt`

| Action       | Command              |
|--------------|----------------------|
| Run          | `python -m src.main` |
| Test         | `pytest`             |
| Lint         | `flake8 src/ tests/` |
| Format       | `black src/ tests/`  |
| Sort imports | `isort src/ tests/`  |
