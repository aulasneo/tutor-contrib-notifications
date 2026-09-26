"""Regression checks for Verawood jobs and an isolated Tutor environment."""

import itertools
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

import click
import jinja2
import yaml
from tutor import hooks

from tutornotifications import plugin


class PluginTests(unittest.TestCase):
    def test_commands_and_config(self) -> None:
        commands: dict[str, click.Command] = {}
        for registered in hooks.Filters.CLI_DO_COMMANDS.iterate():
            assert isinstance(registered, click.Command)
            assert registered.name is not None
            commands[registered.name] = registered
        for command in (
            plugin.send_course_update,
            plugin.send_recurring_nudge,
            plugin.process_scheduled_instructor_tasks,
        ):
            assert command.name is not None
            assert command.callback is not None
            self.assertIn(command.name, commands)
            jobs = command.callback()
            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0][0], "lms")
            self.assertIn(command.name.replace("-", "_"), jobs[0][1])
        self.assertNotIn("send-daily-digest", commands)
        self.assertNotIn("send-weekly-digest", commands)
        config = dict(hooks.Filters.CONFIG_DEFAULTS.iterate())
        config.update(hooks.Filters.CONFIG_UNIQUE.iterate())
        for key in (
            "NOTIFICATIONS_SEND_DAILY_DIGEST",
            "NOTIFICATIONS_SEND_WEEKLY_DIGEST",
            "NOTIFICATIONS_WEEKLY_SCHEDULE",
        ):
            self.assertNotIn(key, config)

    def test_cronjob_feature_combinations(self) -> None:
        patches = dict(hooks.Filters.ENV_PATCHES.iterate())
        template = jinja2.Environment(undefined=jinja2.StrictUndefined).from_string(
            patches["k8s-jobs"]
        )
        for updates, nudges, domain in itertools.product(
            (False, True), (False, True), ("", "courses.example.org")
        ):
            with self.subTest(updates=updates, nudges=nudges, domain=domain):
                rendered = template.render(
                    NOTIFICATIONS_SEND_COURSE_UPDATE=updates,
                    NOTIFICATIONS_SEND_RECURRING_NUDGE=nudges,
                    NOTIFICATION_JOBS_SITE_DOMAIN=domain,
                    NOTIFICATIONS_DAILY_SCHEDULE="17 10 * * *",
                    NOTIFICATIONS_INSTRUCTOR_TASKS_SCHEDULE="23 * * * *",
                    DOCKER_IMAGE_OPENEDX="openedx:test",
                )
                jobs = {
                    job["metadata"]["name"]: job
                    for job in yaml.safe_load_all(rendered)
                    if job
                }
                expected = {"scheduled-instructor-tasks"}
                if updates or nudges:
                    expected.add("notifications-emails")
                self.assertEqual(set(jobs), expected)
                self.assertNotIn("send_email_digest", rendered)
                instructor = jobs["scheduled-instructor-tasks"]
                self.assertEqual(instructor["spec"]["schedule"], "23 * * * *")
                self.assertEqual(
                    self.command(instructor),
                    "./manage.py lms process_scheduled_instructor_tasks",
                )
                if updates or nudges:
                    daily = jobs["notifications-emails"]
                    self.assertEqual(daily["spec"]["schedule"], "17 10 * * *")
                    expected_commands = []
                    for enabled, name in (
                        (updates, "send_course_update"),
                        (nudges, "send_recurring_nudge"),
                    ):
                        if enabled:
                            suffix = f" {domain}" if domain else ""
                            expected_commands.append(f"./manage.py lms {name}{suffix}")
                    self.assertEqual(
                        self.command(daily).strip(),
                        "; ".join(expected_commands) + ";",
                    )
                for job in jobs.values():
                    subprocess.run(
                        ["/bin/sh", "-n", "-c", self.command(job)], check=True
                    )

    @staticmethod
    def command(job: dict[str, Any]) -> str:
        container = job["spec"]["jobTemplate"]["spec"]["template"]["spec"][
            "containers"
        ][0]
        command = container["command"][2]
        assert isinstance(command, str)
        return command

    def test_tutor_environment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="notification-jobs-test-") as directory:
            root = Path(directory)
            env = {
                key: value
                for key, value in os.environ.items()
                if not key.startswith("TUTOR_")
            }
            env["TUTOR_PLUGINS_ROOT"] = str(root / "plugins")

            def tutor(*args: str) -> str:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "from tutor.commands.cli import main; main()",
                        "--root",
                        str(root),
                        *args,
                    ],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            tutor("plugins", "enable", "notification-jobs")
            tutor(
                "config",
                "save",
                "--set",
                "NOTIFICATIONS_DAILY_SCHEDULE=17 10 * * *",
                "--set",
                "NOTIFICATIONS_INSTRUCTOR_TASKS_SCHEDULE=23 * * * *",
            )
            jobs_path = root / "env" / "k8s" / "jobs.yml"
            rendered = jobs_path.read_text()
            jobs = {
                job["metadata"]["name"]: job
                for job in yaml.safe_load_all(rendered)
                if job
            }
            self.assertEqual(
                jobs["notifications-emails"]["spec"]["schedule"], "17 10 * * *"
            )
            self.assertIn("scheduled-instructor-tasks", jobs)
            self.assertNotIn("weekly-emails", jobs)
            self.assertNotIn("send_email_digest", rendered)
            for mode in ("local", "k8s"):
                help_text = tutor(mode, "do", "--help")
                for name in (
                    "send-course-update",
                    "send-recurring-nudge",
                    "process-scheduled-instructor-tasks",
                ):
                    self.assertIn(name, help_text)
                self.assertNotIn("send-daily-digest", help_text)
                self.assertNotIn("send-weekly-digest", help_text)
            tutor(
                "config",
                "save",
                "--set",
                "NOTIFICATIONS_SEND_COURSE_UPDATE=false",
                "--set",
                "NOTIFICATIONS_SEND_RECURRING_NUDGE=false",
            )
            rendered = jobs_path.read_text()
            self.assertNotIn("notifications-emails", rendered)
            self.assertIn("scheduled-instructor-tasks", rendered)


if __name__ == "__main__":
    unittest.main()
