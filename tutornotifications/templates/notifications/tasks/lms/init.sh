echo "Enabling notifications"
./manage.py lms waffle_flag --create --everyone notifications.enable_ora_grade_notifications
./manage.py lms waffle_flag --create --everyone notifications.enable_notifications
./manage.py lms waffle_flag --create --everyone notifications.enable_email_notifications
{% if NOTIFICATIONS_ENABLE_GROUPING %}
./manage.py lms waffle_flag --create --everyone notifications.enable_notifications_grouping
{% else %}
./manage.py lms waffle_delete --flags notifications.enable_notifications_grouping
{% endif %}
