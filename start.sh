#!/bin/bash

if [ "$1" == "web" ]; then
  python manage.py migrate --noinput

  exec python manage.py runserver 0.0.0.0:8000
elif [ "$1" == "bot" ]; then
  exec python tg_bot.py
else
  echo "Неизвестный параметр: $1. Используйте 'web' или 'bot'."
  exit 1
fi
