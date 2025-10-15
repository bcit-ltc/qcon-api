from django.apps import AppConfig
from django.conf import settings
import sys
import logging
logger = logging.getLogger(__name__)

class RestapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restapi'

    def ready(self):
        if 'runserver' in sys.argv or 'qcon.asgi:application' in sys.argv:        
            logger.info("APP_VERSION: " + settings.APP_VERSION)
            logger.info("IMAGE_TAG: " + settings.IMAGE_TAG)
            logger.info("IMAGE_NAME: " + settings.IMAGE_NAME)
            if 'runserver' in sys.argv:
                logger.warning("qconapi has started in Dev Mode")
            else:
                logger.info("qconapi has started")
