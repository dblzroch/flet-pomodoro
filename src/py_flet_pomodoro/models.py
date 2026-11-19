"""Domain models for flet-pomodoro."""

from dataclasses import dataclass


@dataclass
class Session:
    """A pomodoro focus session."""

    id: int | None = None
    task: str = ""
    duration_minutes: int = 25
    completed_minutes: int = 0
    status: str = ""  # "planned", "running", "completed", "interrupted"
    created_at: str = ""  # ISO format
