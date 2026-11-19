# flet-pomodoro

> Pomodoro timer with statistics and deep work mode.

[![CI](https://github.com/dblzroch/flet-pomodoro/actions/workflows/ci.yml/badge.svg)](https://github.com/dblzroch/flet-pomodoro/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Pomodoro timer desktop app built with [Flet](https://flet.dev/). Track focus sessions,
view weekly statistics and use deep work mode.

## Quickstart

```bash
# Clone
git clone https://github.com/dblzroch/flet-pomodoro.git
cd flet-pomodoro

# Install (uv)
uv sync --dev

# Run the desktop app
uv run flet-pomodoro
```

## How it works

- **UI**: Flet (Flutter-based) desktop/mobile GUI.
- **Storage**: SQLite database for focus sessions.
- **Features**: Configurable timer (work/break), session history, weekly focus stats,
  deep work mode, export to CSV.
- **Tests**: `pytest` with coverage gate at 80%.
- **CI**: GitHub Actions runs ruff, mypy and pytest on every push/PR.

## Tests & quality

```bash
make test      # pytest with coverage
make lint      # ruff + mypy
make fmt       # ruff format
```

## License

MIT
