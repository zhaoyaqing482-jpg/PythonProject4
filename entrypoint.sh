#!/bin/bash
set -e

# 收集静态文件
python manage.py collectstatic --noinput

# 运行数据库迁移
python manage.py migrate --noinput

# 启动 Gunicorn
exec gunicorn travel_show.wsgi:application --bind 0.0.0.0:$PORT