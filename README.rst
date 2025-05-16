notifications plugin for `Tutor <https://docs.tutor.edly.io>`__
###############################################################

Tutor plugin that enables email notifications for Open edX.
Open edX offers three main types of notifications:

- Course updates
- Recurring nudges
- Daily digests
- Weekly digests

This plugin will enable all of them by default.

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

.. code-block:: bash

    pip install git+https://github.com/aulasneo/tutor-contrib-notifications.git

Usage
*****

To enable the plugin, run:

.. code-block:: bash

    tutor plugins enable notifications
    tutor {local|k8s} do init [--limit notifications
    tutor {local|k8s} start

The `tutor {local|k8s} do init` command will set the waffle flags for the notifications plugin.

You can run the following commands to trigger the notifications manually:

.. code-block:: bash

    tutor {local|k8s} do send-daily-digest
    tutor {local|k8s} do send-weekly-digest
    tutor {local|k8s} do send-course-update
    tutor {local|k8s} do send-recurring-nudge

For Kubernetes users, this plugin will setup a cronjob to run the daily and weekly digests
at the configured schedules. Users of a tutor local installation will have to set up a cronjob
manually.

Configuration
*************

- NOTIFICATIONS_DAILY_SCHEDULE: Set the schedule for the daily emails. Default is "0 10 \* \* \*" (every day at 10am UTC).
- NOTIFICATIONS_WEEKLY_SCHEDULE: Set the schedule for the weekly emails. Default is "0 10 \* \* 0" (every Sunday at 10am UTC).
- NOTIFICATIONS_SEND_COURSE_UPDATE: Enable course updates. Default is True.
- NOTIFICATIONS_SEND_RECURRING_NUDGE: Enable recurring nudges. Default is True.
- NOTIFICATIONS_SEND_DAILY_DIGEST: Enable daily digests. Default is True.
- NOTIFICATIONS_SEND_WEEKLY_DIGEST: Enable weekly digests. Default is True.
- NOTIFICATIONS_ENABLE_ORA_GRADE_NOTIFICATIONS: Enable ORA grade notifications. Default is True.
- NOTIFICATIONS_ENABLE_NOTIFICATIONS: Enable notifications. Default is True.
- NOTIFICATIONS_ENABLE_EMAIL_NOTIFICATIONS: Enable email notifications. Default is True.
- NOTIFICATIONS_ENABLE_GROUPING: Enable grouping. Default is True.
- NOTIFICATIONS_DEFAULT_FROM_EMAIL: Set the default from email. Default is "{{ CONTACT_EMAIL }}".

Notes:

- After modifying NOTIFICATIONS_ENABLE_GROUPING, you will need to run `tutor {local|k8s} do init --limit notifications` to apply the changes.
- After changing the schedules, you will need to restart the cronjobs with `tutor k8s start`.


License
*******

This software is licensed under the terms of the AGPLv3.
