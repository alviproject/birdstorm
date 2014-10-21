from game.utils.config import config
from django.conf import settings


def analytics(_):
    return dict(
        UA=config.ANALYTICS_UA,
        SUBDOMAINS=settings.SUBDOMAINS,
        DOMAIN_NAME=settings.DOMAIN_NAME,
    )