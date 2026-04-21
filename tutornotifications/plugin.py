from glob import glob

import click
import importlib_resources
from tutor import hooks

from .__about__ import __version__

########################################
# CONFIGURATION
########################################

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("NOTIFICATIONS_VERSION", __version__),
        ("NOTIFICATIONS_DAILY_SCHEDULE", "0 10 * * *"),
        ("NOTIFICATIONS_WEEKLY_SCHEDULE", "0 10 * * 0"),
        ("NOTIFICATION_JOBS_SITE_DOMAIN", "{{ LMS_HOST }}"),
        ("NOTIFICATIONS_SEND_COURSE_UPDATE", True),
        ("NOTIFICATIONS_SEND_RECURRING_NUDGE", True),
        ("NOTIFICATIONS_SEND_DAILY_DIGEST", True),
        ("NOTIFICATIONS_SEND_WEEKLY_DIGEST", True),
    ]
)

########################################
# PATCH LOADING
########################################

for path in glob(
    str(importlib_resources.files("tutornotifications") / "patches" / "*")
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((path.rsplit("/", 1)[-1], patch_file.read()))


########################################
# CUSTOM JOBS (a.k.a. "do-commands")
########################################


@click.command()
def send_daily_digest() -> list[tuple[str, str]]:
    """
    Send daily digest emails.
    """
    return [
        ("lms", "./manage.py lms send_email_digest Daily"),
    ]


@click.command()
def send_weekly_digest() -> list[tuple[str, str]]:
    """
    Send weekly digest emails.
    """
    return [
        ("lms", "./manage.py lms send_email_digest Weekly"),
    ]


@click.command()
def send_course_update() -> list[tuple[str, str]]:
    """
    Send course update emails.
    """
    return [
        (
            "lms",
            "./manage.py lms send_course_update"
            "{% if NOTIFICATION_JOBS_SITE_DOMAIN %} {{ NOTIFICATION_JOBS_SITE_DOMAIN }}{% endif %}",
        ),
    ]


@click.command()
def send_recurring_nudge() -> list[tuple[str, str]]:
    """
    Send recurring nudge emails.
    """
    return [
        (
            "lms",
            "./manage.py lms send_recurring_nudge"
            "{% if NOTIFICATION_JOBS_SITE_DOMAIN %} {{ NOTIFICATION_JOBS_SITE_DOMAIN }}{% endif %}",
        ),
    ]


hooks.Filters.CLI_DO_COMMANDS.add_item(send_daily_digest)
hooks.Filters.CLI_DO_COMMANDS.add_item(send_weekly_digest)
hooks.Filters.CLI_DO_COMMANDS.add_item(send_course_update)
hooks.Filters.CLI_DO_COMMANDS.add_item(send_recurring_nudge)
