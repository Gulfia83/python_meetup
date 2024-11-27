#!/bin/bash

if [ "$1" == "web" ]; then
  python manage.py migrate --noinput

  python manage.py createsuperuser --noinput \
    --username root \
    --email admin@example.com \
    --password root

  exec python manage.py runserver 0.0.0.0:8000
elif [ "$1" == "bot" ]; then
  exec python tg_bot.py
else
  echo "Неизвестный параметр: $1. Используйте 'web' или 'bot'."
  exit 1
fi
