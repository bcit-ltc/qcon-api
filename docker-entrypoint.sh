#!/usr/bin/env sh
set -e


echo "Listing /etc/secrets contents (if present)..."
if [ -d /etc/secrets ]; then
  ls -al /etc/secrets
else
  echo "/etc/secrets directory does not exist"
fi

echo "-------------------------------------------------------------------------------------------"
echo "Container is now PAUSED for troubleshooting."
echo "You can exec into this pod and run migrations manually, e.g.:"
echo "  python manage.py makemigrations api"
echo "  python manage.py migrate"
echo "Sleeping for 600 seconds (10 minutes)..."
sleep 600
echo "Resuming normal startup sequence..."

>&2 echo "make Database migrations"
python manage.py makemigrations api
echo "-------------------------------------------------------------------------------------------\n"

>&2 echo "Run Database migrations"
python manage.py migrate
echo "-------------------------------------------------------------------------------------------\n"

# Collect static files
>&2 echo "Collect static"
python manage.py collectstatic --noinput

>&2 echo "Starting redis"
redis-server --daemonize yes

>&2 echo "Starting Celery"
celery -A qcon worker --loglevel=DEBUG --concurrency=4 -n worker1@%h --detach worker_hijack_root_logger=False worker_redirect_stdouts=True worker_redirect_stdouts_level=DEBUG
celery -A qcon worker --loglevel=DEBUG --concurrency=4 -n worker2@%h --detach worker_hijack_root_logger=False worker_redirect_stdouts=True worker_redirect_stdouts_level=DEBUG
celery -A qcon worker --loglevel=DEBUG --concurrency=4 -n worker3@%h --detach worker_hijack_root_logger=False worker_redirect_stdouts=True worker_redirect_stdouts_level=DEBUG
celery -A qcon worker --loglevel=DEBUG --concurrency=4 -n worker4@%h --detach worker_hijack_root_logger=False worker_redirect_stdouts=True worker_redirect_stdouts_level=DEBUG

>&2 echo "Starting Daphne/Runserver"
exec "$@"
