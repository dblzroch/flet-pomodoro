"""Flet UI for flet-pomodoro.  # pragma: no cover"""

from pathlib import Path

import flet as ft

from py_flet_pomodoro.database import Database
from py_flet_pomodoro.models import Session


def app_main(page: ft.Page) -> None:  # pragma: no cover
    """Build the Flet UI."""
    page.title = "py-pomodoro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400  # type: ignore[attr-defined]
    page.window_height = 650  # type: ignore[attr-defined]

    db = Database(Path.home() / ".local" / "share" / "flet-pomodoro" / "pomodoro.db")

    # --- UI state ---
    task_field = ft.TextField(label="Tarefa", width=300)
    duration_field = ft.TextField(
        label="Duração (min)",
        value="25",
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    timer_text = ft.Text("25:00", size=48, weight=ft.FontWeight.BOLD)
    status_text = ft.Text("Pronto para começar", size=14, color=ft.colors.GREY_600)
    stats_text = ft.Text(size=14)

    sessions_list = ft.ListView(expand=True, spacing=8, padding=20)

    def refresh() -> None:
        """Refresh the UI from the database."""
        sessions = db.get_sessions()
        sessions_list.controls.clear()

        for s in sessions:
            sessions_list.controls.append(
                ft.ListTile(
                    title=ft.Text(s.task, weight=ft.FontWeight.W_500),
                    subtitle=ft.Text(
                        f"{s.completed_minutes}/{s.duration_minutes} min — {s.status}",
                        size=12,
                        color=ft.colors.GREY_600,
                    ),
                    trailing=ft.Text(s.created_at[:10], size=11),
                )
            )

        total = db.total_focus_minutes()
        count = db.sessions_count()
        stats_text.value = f"Esta semana: {count} sessões, {total} min focados"

        page.update()

    def start_session(e: ft.ControlEvent) -> None:
        """Start a new pomodoro session."""
        if not task_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("Informe uma tarefa"))  # type: ignore[attr-defined]
            page.snack_bar.open = True  # type: ignore[attr-defined]
            page.update()
            return

        try:
            duration = int(duration_field.value or 25)
        except ValueError:
            duration = 25

        session = Session(
            task=task_field.value,
            duration_minutes=duration,
            completed_minutes=0,
            status="running",
            created_at=db._now(),
        )
        db.add_session(session)

        task_field.value = ""
        refresh()

    def export_csv(e: ft.ControlEvent) -> None:
        """Export all sessions as CSV text."""
        sessions = db.get_sessions()
        lines = ["task,duration_minutes,completed_minutes,status,created_at"]
        for s in sessions:
            lines.append(
                f"{s.task},{s.duration_minutes},{s.completed_minutes},{s.status},{s.created_at}"
            )
        page.snack_bar = ft.SnackBar(ft.Text("\n".join(lines)[:400]))  # type: ignore[attr-defined]
        page.snack_bar.open = True  # type: ignore[attr-defined]
        page.update()

    # --- Layout ---
    page.add(
        ft.Text("Pomodoro", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row(
            [
                task_field,
                duration_field,
                ft.ElevatedButton("Iniciar", on_click=start_session),
            ],
            wrap=True,
        ),
        timer_text,
        status_text,
        ft.Divider(),
        stats_text,
        ft.Divider(),
        ft.Text("Sessões", size=18, weight=ft.FontWeight.BOLD),
        sessions_list,
        ft.ElevatedButton("Exportar CSV", on_click=export_csv),
    )

    refresh()
