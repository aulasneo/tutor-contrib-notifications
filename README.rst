notifications plugin for `Tutor <https://docs.tutor.edly.io>`__
###############################################################

Tutor companion plugin for Open edX notification jobs on Ulmo / Tutor 21.x.

This repository is meant to be installed alongside the official
`openedx/tutor-contrib-platform-notifications <https://github.com/openedx/tutor-contrib-platform-notifications>`__
plugin.

The official plugin provides the notification tray, MFE integration and core
notification configuration under the Tutor plugin name ``notifications``.
This repository complements it under the Tutor plugin name ``notification-jobs``
by keeping job automation for notification-related management commands:

- Course updates
- Recurring nudges
- Daily digests
- Weekly digests
- Scheduled instructor tasks

This plugin will expose manual Tutor jobs for all of them and, on Kubernetes,
will create CronJobs for the scheduled digests.

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

Notifications help you stay updated on important activity in your courses. You can receive notifications via the notification tray in real time, or through email summaries delivered periodically.

Notifications are sent daily and weekly, and can be configured in the account settings page.

Event that trigger notifications are course updates, forum activities and ORA submissions.


To learn more about this feature, see `Email Notifications <https://docs.openedx.org/en/latest/learners/sfd_notifications/index.html>`__.

Installation
************

Install both the official notifications plugin and this companion plugin.

.. code-block:: bash

    pip install git+https://github.com/openedx/tutor-contrib-platform-notifications.git
    pip install git+https://github.com/aulasneo/tutor-contrib-notifications.git

Usage
*****

Enable both plugins:

.. code-block:: bash

    tutor plugins enable notifications
    tutor plugins enable notification-jobs
    tutor {local|k8s} do init --limit notifications
    tutor {local|k8s} start

This plugin adds the following manual jobs:

.. code-block:: bash

    tutor {local|k8s} do send-daily-digest
    tutor {local|k8s} do send-weekly-digest
    tutor {local|k8s} do process-scheduled-instructor-tasks
    tutor {local|k8s} do send-course-update
    tutor {local|k8s} do send-recurring-nudge

For Kubernetes users, this plugin sets up CronJobs to run daily and weekly
digests plus scheduled instructor tasks at the configured schedules. Users of a
Tutor local installation will still have to configure cron outside Tutor.

Configuration
*************

- NOTIFICATIONS_DAILY_SCHEDULE: Set the schedule for the daily emails. Default is "<random-minute> 10 \* \* \*" (every day at 10 UTC, with a randomized minute).
- NOTIFICATIONS_INSTRUCTOR_TASKS_SCHEDULE: Set the schedule for scheduled instructor tasks. Default is "<random-minute> \* \* \* \*" (every hour, with a randomized minute).
- NOTIFICATIONS_WEEKLY_SCHEDULE: Set the schedule for the weekly emails. Default is "<random-minute> 10 \* \* 0" (every Sunday at 10 UTC, with a randomized minute).
- NOTIFICATION_JOBS_SITE_DOMAIN: Optional site domain passed to `send-course-update` and `send-recurring-nudge`. Default is "{{ LMS_HOST }}". Set it to an empty value to run those jobs for all sites.
- NOTIFICATIONS_SEND_COURSE_UPDATE: Enable course updates. Default is True.
- NOTIFICATIONS_SEND_RECURRING_NUDGE: Enable recurring nudges. Default is True.
- NOTIFICATIONS_SEND_DAILY_DIGEST: Enable daily digests. Default is True.
- NOTIFICATIONS_SEND_WEEKLY_DIGEST: Enable weekly digests. Default is True.

Notes:

- The default randomized minute spreads CronJob launches across clusters with many sites, which helps avoid large bursts of pods starting at the same time.
- If you want a fixed execution time instead of a randomized minute, set the corresponding schedule variable explicitly in your Tutor config.
- After changing the schedules, you will need to restart the cronjobs with `tutor k8s start`.


License
*******

This software is licensed under the terms of the AGPLv3.
