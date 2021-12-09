#! /bin/bash
apt -yqq install gcc rabbitmq-server
yes | cp -f /home/site/wwwroot/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
service rabbitmq-server start

cd /home/site/wwwroot
pip install -r requirements.txt

celery multi start w1 -A achadosepedidos -l info

#gunicorn --bind=0.0.0.0 --timeout 600 achadosepedidos.wsgi
gunicorn --workers 4 --threads 2 --bind=0.0.0.0 --timeout 600 --access-logfile '/tmp/django-access.log' --error-logfile '/tmp/django-error.log' achadosepedidos.wsgi