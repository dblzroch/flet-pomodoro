"""CLI entry point for flet-pomodoro."""

from flet import app as ft_app

from py_flet_pomodoro.main import app_main as flet_main


def main() -> None:
    """Launch the Flet desktop app."""
    ft_app(target=flet_main)  # type: ignore[operator]


if __name__ == "__main__":  # pragma: no cover
    main()
