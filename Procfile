web: sh -c 'cd gen_zone && python manage.py migrate && python manage.py collectstatic --noinput && pip install -r requirements.txt && DJANGO_SETTINGS_MODULE=gen_zone.settings uvicorn --ws=websockets gen_zone.asgi:application'