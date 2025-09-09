import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qcon.settings")
app = Celery("qcon")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()