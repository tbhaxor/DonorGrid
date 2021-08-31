#!/bin/sh

set -e
sleep 10
python manage.py migrate
USER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='${DG_USER:-donorgrid}').count())")
if [ "$USER_COUNT" -eq 0 ]
then
  python manage.py shell -c "from django.contrib.auth.models import User; user = User.objects.create_superuser(username='${DG_USER:-donorgrid}', email='${DG_EMAIL:-donorgrid@example.com}'); user.set_password('${DG_PASS:-donorgrid}'); user.is_superuser = True; user.save()"
else
  echo User "${DG_USER:-donorgrid}" already exists
fi
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000