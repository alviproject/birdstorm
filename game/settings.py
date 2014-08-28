"""
Django settings for game project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
# TODO https://docs.djangoproject.com/en/dev/howto/deployment/checklist/
from math import sqrt

import os
import game
from game.utils import config


PROJECT_DIR = os.path.dirname(game.__file__)
BASE_DIR = os.path.dirname(PROJECT_DIR)

# TODO assert if empty and debug is set to False
SECRET_KEY = config.secret_key or '00000000000000000000000000000000000000000000000000'

DEBUG = config.debug

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.sites',
    #'sorl.thumbnail',
    'pybb',
    'rest_framework',
    'rest_framework.authtoken',
    'kombu.transport.django',  # required for celery django broker
    'game.apps.account',
    'game.apps.chat',
    'game.apps.core',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pybb.middleware.PybbMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware', #TODO this shall be before or after PybbMiddleware?
)


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'game.apps.account.auth_backend.AuthBackend',
)

ROOT_URLCONF = 'game.urls'

WSGI_APPLICATION = 'game.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config.db_engine or 'django.db.backends.sqlite3',
        'NAME': config.db_name or os.path.join(PROJECT_DIR, 'data', 'db.sqlite3'),
        'USER': config.db_user,
        'PASSWORD': config.db_password,
        'HOST': config.db_host,
        'PORT': config.db_port,
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(PROJECT_DIR, "static_generated")

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "static"),
)

TEMPLATE_DIRS = (os.path.join(PROJECT_DIR, 'templates'), )

ANONYMOUS_USER_ID = 1  #TODO

REST_FRAMEWORK = {
    #'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 2048,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

BROKER_URL = 'django://'

FACTOR = sqrt(2)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'pybb.context_processors.processor',
    "game.utils.context_processors.analytics"
)

SITE_ID = 1


PYBB_PERMISSION_HANDLER = 'game.apps.account.forum.ForumPermissionHandler'
