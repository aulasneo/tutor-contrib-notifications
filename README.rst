notifications plugin for `Tutor <https://docs.tutor.edly.io>`__
###############################################################

Tutor plugin for Open edX notification jobs on Verawood / Tutor 22.x.

This repository provides the Tutor plugin ``notification-jobs`` to automate
the following management commands:

- Course updates
- Recurring nudges
- Scheduled instructor tasks

This plugin exposes manual Tutor jobs for all of them and, on Kubernetes,
creates CronJobs for daily course updates and recurring nudges, plus hourly
scheduled instructor tasks.

Course updates (aka course highlight emails)
============================================

If your Open edX system adminstrator has configured your instance of the Open edX platform to send course highlight emails, you can send automatic email messages to learners in your course that contain three to five “highlights” of upcoming course content. A highlight is a brief description of an important concept, idea, or activity in the section. Your Open edX system administrator provides the template for this course highlight email, and you enter the highlights for the email in Studio.

To learn more about this feature, see `Course Highlight Email <https://docs.openedx.org/en/latest/educators/how-tos/course_development/manage_course_highlight_emails.html#manage-course-highlight-emails>`__.

Recurring nudges
================

Recurring nudges are emails that are sent 3 and 10 days after a learner enrolls in a course. 

To learn more about this feature, see `Recurring Nudges <https://docs.openedx.org/en/latest/educators/references/communication/automatic_email.html#guide-to-automatic-email-messages>`__.

Email notifications
===================

On Verawood, notification tray integration is provided by ``tutor-mfe``.
The separate ``tutor-contrib-platform-notifications`` plugin is no longer needed.

Open edX schedules daily and weekly notification digests automatically through
delayed Celery tasks when notifications are created. This plugin does not
schedule digests; the ``send_email_digest`` management command is deprecated.

To learn more about this feature, see `Email Notifications <https://docs.openedx.org/en/latest/learners/sfd_notifications/index.html>`__.

Installation
************

Install this plugin:

.. code-block:: bash

    pip install git+https://github.com/aulasneo/tutor-contrib-notifications.git

Usage
*****

Enable the jobs plugin and regenerate the environment:

.. code-block:: bash

    tutor plugins enable notification-jobs
    tutor config save
    tutor {local|k8s} start

This plugin adds the following manual jobs:

.. code-block:: bash

    tutor {local|k8s} do process-scheduled-instructor-tasks
    tutor {local|k8s} do send-course-update
    tutor {local|k8s} do send-recurring-nudge

For Kubernetes users, this plugin sets up CronJobs to run course updates,
recurring nudges, and scheduled instructor tasks at the configured schedules. Users of a
Tutor local installation will still have to configure cron outside Tutor.

Upgrading from Tutor 21
***********************

- Disable the old ``notifications`` plugin before uninstalling
  ``tutor-contrib-platform-notifications``. Use ``tutor-mfe`` for notification
  tray integration on Tutor 22.
- Remove external cron entries calling ``send_email_digest``,
  ``send-daily-digest``, or ``send-weekly-digest``.
- Remove the unused ``NOTIFICATIONS_SEND_DAILY_DIGEST``,
  ``NOTIFICATIONS_SEND_WEEKLY_DIGEST``, and ``NOTIFICATIONS_WEEKLY_SCHEDULE``
  keys from your Tutor configuration.
- Run ``tutor config save`` and ``tutor k8s start`` to update the remaining
  Kubernetes jobs. Delete the obsolete ``weekly-emails`` CronJob if it still
  exists in your Tutor namespace. If both course updates and recurring nudges
  are disabled, also delete any existing ``notifications-emails`` CronJob.

The ``NOTIFICATIONS_DAILY_SCHEDULE`` setting is retained for course updates
and recurring nudges.

Configuration
*************

- NOTIFICATIONS_DAILY_SCHEDULE: Set the schedule for course updates and recurring nudges. Default is "<random-minute> 10 \* \* \*" (every day at 10 UTC, with a randomized minute).
- NOTIFICATIONS_INSTRUCTOR_TASKS_SCHEDULE: Set the schedule for scheduled instructor tasks. Default is "<random-minute> \* \* \* \*" (every hour, with a randomized minute).
- NOTIFICATION_JOBS_SITE_DOMAIN: Optional site domain passed to `send-course-update` and `send-recurring-nudge`. Default is "{{ LMS_HOST }}". Set it to an empty value to run those jobs for all sites.
- NOTIFICATIONS_SEND_COURSE_UPDATE: Enable course updates. Default is True.
- NOTIFICATIONS_SEND_RECURRING_NUDGE: Enable recurring nudges. Default is True.

Notes:

- The daily email CronJob is only generated when course updates or recurring nudges are enabled.
- The default randomized minute spreads CronJob launches across clusters with many sites, which helps avoid large bursts of pods starting at the same time.
- If you want a fixed execution time instead of a randomized minute, set the corresponding schedule variable explicitly in your Tutor config.
- After changing the schedules, you will need to restart the cronjobs with `tutor k8s start`.


Development
***********

In your Python virtual environment, install the development dependencies and
run the checks:

.. code-block:: bash

    make requirements
    make test

You can select a specific virtual environment with
``make requirements test PYTHON=/path/to/venv/bin/python``.
Packaging checks and Tutor integration tests use temporary directories, leaving
your workspace's ``config.yml``, ``env/``, and ``dist/`` intact.
CI runs the suite on Python 3.10 through 3.14.

License
*******

This software is licensed under the terms of the AGPLv3.
