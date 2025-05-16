import os
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
        # Add your new settings that have default values here.
        # Each new setting is a pair: (setting_name, default_value).
        # Prefix your setting names with 'NOTIFICATIONS_'.
        ("NOTIFICATIONS_VERSION", __version__),
        ("NOTIFICATIONS_DAILY_SCHEDULE", "0 10 * * *"),
        ("NOTIFICATIONS_WEEKLY_SCHEDULE", "0 10 * * 0"),
        ("NOTIFICATIONS_SEND_COURSE_UPDATE", True),
        ("NOTIFICATIONS_SEND_RECURRING_NUDGE", True),
        ("NOTIFICATIONS_SEND_DAILY_DIGEST", True),
        ("NOTIFICATIONS_SEND_WEEKLY_DIGEST", True),
        ("NOTIFICATIONS_ENABLE_GROUPING", True),
        ("NOTIFICATIONS_DEFAULT_FROM_EMAIL", "{{ CONTACT_EMAIL }}"),
    ]
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        # Add settings that don't have a reasonable default for all users here.
        # For instance: passwords, secret keys, etc.
        # Each new setting is a pair: (setting_name, unique_generated_value).
        # Prefix your setting names with 'NOTIFICATIONS_'.
        # For example:
        ### ("NOTIFICATIONS_SECRET_KEY", "{{ 24|random_string }}"),
    ]
)

hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        # Danger zone!
        # Add values to override settings from Tutor core or other plugins here.
        # Each override is a pair: (setting_name, new_value). For example:
        ### ("PLATFORM_NAME", "My platform"),
    ]
)


########################################
# INITIALIZATION TASKS
########################################

# To add a custom initialization task, create a bash script template under:
# tutornotifications/templates/notifications/tasks/
# and then add it to the MY_INIT_TASKS list. Each task is in the format:
# ("<service>", ("<path>", "<to>", "<script>", "<template>"))
MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    # For example, to add LMS initialization steps, you could add the script template at:
    # tutornotifications/templates/notifications/tasks/lms/init.sh
    # And then add the line:
    ("lms", ("notifications", "tasks", "lms", "init.sh")),
]


# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the CLI_DO_INIT_TASKS filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path in MY_INIT_TASKS:
    full_path: str = str(
        importlib_resources.files("tutornotifications")
        / os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task))


########################################
# DOCKER IMAGE MANAGEMENT
########################################


# Images to be built by `tutor images build`.
# Each item is a quadruple in the form:
#     ("<tutor_image_name>", ("path", "to", "build", "dir"), "<docker_image_tag>", "<build_args>")
hooks.Filters.IMAGES_BUILD.add_items(
    [
        # To build `myimage` with `tutor images build myimage`,
        # you would add a Dockerfile to templates/notifications/build/myimage,
        # and then write:
        ### (
        ###     "myimage",
        ###     ("plugins", "notifications", "build", "myimage"),
        ###     "docker.io/myimage:{{ NOTIFICATIONS_VERSION }}",
        ###     (),
        ### ),
    ]
)


# Images to be pulled as part of `tutor images pull`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PULL.add_items(
    [
        # To pull `myimage` with `tutor images pull myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ NOTIFICATIONS_VERSION }}",
        ### ),
    ]
)


# Images to be pushed as part of `tutor images push`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PUSH.add_items(
    [
        # To push `myimage` with `tutor images push myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ NOTIFICATIONS_VERSION }}",
        ### ),
    ]
)


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        str(importlib_resources.files("tutornotifications") / "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``source_path/destination_path`` (relative to your Tutor environment).
    # For example, ``tutornotifications/templates/notifications/build``
    # will be rendered to ``$(tutor config printroot)/env/plugins/notifications/build``.
    [
        ("notifications/build", "plugins"),
        ("notifications/apps", "plugins"),
    ],
)


########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in tutornotifications/patches,
# apply a patch based on the file's name and contents.
for path in glob(str(importlib_resources.files("tutornotifications") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))


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
        ("lms", "./manage.py lms send_course_update {{ LMS_HOST }}"),
    ]

@click.command()
def send_recurring_nudge() -> list[tuple[str, str]]:
    """
    Send recurring nudge emails.
    """
    return [
        ("lms", "./manage.py lms send_recurring_nudge {{ LMS_HOST }}"),
    ]

hooks.Filters.CLI_DO_COMMANDS.add_item(send_daily_digest)
hooks.Filters.CLI_DO_COMMANDS.add_item(send_weekly_digest)
hooks.Filters.CLI_DO_COMMANDS.add_item(send_course_update)
hooks.Filters.CLI_DO_COMMANDS.add_item(send_recurring_nudge)


#######################################
# CUSTOM CLI COMMANDS
#######################################

# Your plugin can also add custom commands directly to the Tutor CLI.
# These commands are run directly on the user's host computer
# (unlike jobs, which are run in containers).

# To define a command group for your plugin, you would define a Click
# group and then add it to CLI_COMMANDS:


### @click.group()
### def notifications() -> None:
###     pass


### hooks.Filters.CLI_COMMANDS.add_item(notifications)


# Then, you would add subcommands directly to the Click group, for example:


### @notifications.command()
### def example_command() -> None:
###     """
###     This is helptext for an example command.
###     """
###     print("You've run an example command.")


# This would allow you to run:
#   $ tutor notifications example-command
