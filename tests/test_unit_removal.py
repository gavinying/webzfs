"""Scheduler unit removal can use a deployment-supplied helper instead of `sudo rm`."""
import pytest

from services import job_scheduler


@pytest.mark.parametrize("remover, expected", [
    (None, ["sudo", "rm", "-f"]),
    ("", ["sudo", "rm", "-f"]),
    ("/usr/local/libexec/webzfs-remove-unit", ["sudo", "/usr/local/libexec/webzfs-remove-unit"]),
])
def test_unit_removal_command(monkeypatch, remover, expected):
    if remover is None:
        monkeypatch.delenv("WEBZFS_UNIT_REMOVER", raising=False)
    else:
        monkeypatch.setenv("WEBZFS_UNIT_REMOVER", remover)
    commands = []
    monkeypatch.setattr(job_scheduler.subprocess, "run", lambda argv, **_: commands.append(argv))
    scheduler = job_scheduler.TaskScheduler.__new__(job_scheduler.TaskScheduler)
    monkeypatch.setattr(scheduler, "_systemctl", lambda *args, **kwargs: None)

    scheduler._remove_units_by_base_name("webzfs-task-scrub-1")

    paths = [f"{job_scheduler.SYSTEMD_UNIT_DIR}/webzfs-task-scrub-1.{kind}" for kind in ("service", "timer")]
    assert commands == [expected + [path] for path in paths]
