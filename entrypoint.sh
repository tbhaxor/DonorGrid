#!/bin/sh

set -e
sleep 10
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; user = User.objects.create_superuser(username='${DG_USER:-donorgrid}', email='${DG_EMAIL:-donorgrid@example.com}'); user.set_password('${DG_PASS:-donorgrid}'); user.is_superuser = True; user.save()"
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000