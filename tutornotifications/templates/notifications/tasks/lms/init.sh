echo "Enabling notifications"
{% if NOTIFICATIONS_ENABLE_ORA_GRADE_NOTIFICATIONS %}
./manage.py lms waffle_flag --create --everyone notifications.enable_ora_grade_notifications
{% else %}
./manage.py lms waffle_delete --flags notifications.enable_ora_grade_notifications
{% endif %}
{% if NOTIFICATIONS_ENABLE_NOTIFICATIONS %}
./manage.py lms waffle_flag --create --everyone notifications.enable_notifications
{% else %}
./manage.py lms waffle_delete --flags notifications.enable_notifications
{% endif %}
{% if NOTIFICATIONS_ENABLE_EMAIL_NOTIFICATIONS %}
./manage.py lms waffle_flag --create --everyone notifications.enable_email_notifications
{% else %}
./manage.py lms waffle_delete --flags notifications.enable_email_notifications
{% endif %}
{% if NOTIFICATIONS_ENABLE_GROUPING %}
./manage.py lms waffle_flag --create --everyone notifications.enable_notifications_grouping
{% else %}
./manage.py lms waffle_delete --flags notifications.enable_notifications_grouping
{% endif %}
