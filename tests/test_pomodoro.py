"""Tests for flet-pomodoro database and models."""

from datetime import date, timedelta

from py_flet_pomodoro.database import Database
from py_flet_pomodoro.models import Session


# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------
def test_session_defaults():
    s = Session(task="Estudar", duration_minutes=25, status="planned")
    assert s.task == "Estudar"
    assert s.duration_minutes == 25
    assert s.completed_minutes == 0
    assert s.status == "planned"
    assert s.id is None


# ------------------------------------------------------------------
# Database: sessions CRUD
# ------------------------------------------------------------------
def test_add_and_get_session(tmp_path):
    db = Database(tmp_path / "test.db")
    rid = db.add_session(
        Session(
            task="Estudar",
            duration_minutes=25,
            status="running",
            created_at="2024-01-01T10:00:00",
        )
    )
    assert rid == 1

    s = db.get_session(1)
    assert s is not None
    assert s.task == "Estudar"
    assert s.duration_minutes == 25
    assert s.status == "running"


def test_get_session_not_found(tmp_path):
    db = Database(tmp_path / "test.db")
    assert db.get_session(999) is None


def test_get_sessions_ordered(tmp_path):
    db = Database(tmp_path / "test.db")
    db.add_session(
        Session(
            task="A",
            duration_minutes=25,
            created_at="2024-01-01T10:00:00",
        )
    )
    db.add_session(
        Session(
            task="B",
            duration_minutes=25,
            created_at="2024-01-02T10:00:00",
        )
    )

    sessions = db.get_sessions()
    assert len(sessions) == 2
    assert sessions[0].task == "B"


def test_update_session(tmp_path):
    db = Database(tmp_path / "test.db")
    rid = db.add_session(Session(task="Velho", duration_minutes=25, status="planned"))
    session_update = Session(
        id=rid, task="Novo", duration_minutes=50, status="completed"
    )
    assert db.update_session(session_update) is True
    s = db.get_session(rid)
    assert s is not None
    assert s.task == "Novo"
    assert s.duration_minutes == 50
    assert s.status == "completed"


def test_delete_session(tmp_path):
    db = Database(tmp_path / "test.db")
    rid = db.add_session(Session(task="Temp", duration_minutes=25))
    assert db.delete_session(rid) is True
    assert db.get_sessions() == []


# ------------------------------------------------------------------
# Database: sessions by date
# ------------------------------------------------------------------
def test_get_sessions_by_date(tmp_path):
    db = Database(tmp_path / "test.db")
    db.add_session(
        Session(
            task="Hoje",
            duration_minutes=25,
            created_at="2024-01-15T10:00:00",
        )
    )
    db.add_session(
        Session(
            task="Ontem",
            duration_minutes=25,
            created_at="2024-01-14T10:00:00",
        )
    )

    today = db.get_sessions_by_date("2024-01-15")
    assert len(today) == 1
    assert today[0].task == "Hoje"


# ------------------------------------------------------------------
# Database: statistics
# ------------------------------------------------------------------
def test_total_focus_minutes(tmp_path):
    db = Database(tmp_path / "test.db")
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    db.add_session(
        Session(
            task="A",
            duration_minutes=25,
            completed_minutes=25,
            status="completed",
            created_at=f"{today}T10:00:00",
        )
    )
    db.add_session(
        Session(
            task="B",
            duration_minutes=25,
            completed_minutes=10,
            status="completed",
            created_at=f"{yesterday}T10:00:00",
        )
    )
    db.add_session(
        Session(
            task="C",
            duration_minutes=25,
            completed_minutes=0,
            status="interrupted",
            created_at=f"{today}T11:00:00",
        )
    )

    assert db.total_focus_minutes(days=7) == 35


def test_sessions_count(tmp_path):
    db = Database(tmp_path / "test.db")
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    db.add_session(
        Session(
            task="A",
            duration_minutes=25,
            completed_minutes=25,
            status="completed",
            created_at=f"{today}T10:00:00",
        )
    )
    db.add_session(
        Session(
            task="B",
            duration_minutes=25,
            completed_minutes=25,
            status="completed",
            created_at=f"{yesterday}T10:00:00",
        )
    )
    db.add_session(
        Session(
            task="C",
            duration_minutes=25,
            completed_minutes=0,
            status="running",
            created_at=f"{today}T11:00:00",
        )
    )

    assert db.sessions_count(days=7) == 2


def test_daily_stats(tmp_path):
    db = Database(tmp_path / "test.db")
    today = date.today().isoformat()
    db.add_session(
        Session(
            task="A",
            duration_minutes=25,
            completed_minutes=25,
            status="completed",
            created_at=f"{today}T10:00:00",
        )
    )
    db.add_session(
        Session(
            task="B",
            duration_minutes=25,
            completed_minutes=15,
            status="completed",
            created_at=f"{today}T11:00:00",
        )
    )
    db.add_session(
        Session(
            task="C",
            duration_minutes=25,
            completed_minutes=25,
            status="completed",
            created_at=f"{today}T12:00:00",
        )
    )

    stats = db.daily_stats(days=7)
    by_day = dict(stats)
    assert by_day.get(today) == 65


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
def test_cli_main(monkeypatch):
    """Test that cli.main calls ft.app with the right target."""
    import py_flet_pomodoro.cli as cli_mod

    called = {}

    def fake_app(target):
        called["target"] = target

    monkeypatch.setattr(cli_mod, "ft_app", fake_app)
    cli_mod.main()
    assert callable(called.get("target"))
