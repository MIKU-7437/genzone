web: sh -c 'cd gen_zone && python manage.py migrate && python manage.py collectstatic --noinput && pip install -r requirements.txt && uvicorn --log-level debug gen_zone.asgi:application'