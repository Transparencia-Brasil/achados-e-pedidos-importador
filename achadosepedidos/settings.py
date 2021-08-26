"""
Django settings for achadosepedidos project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = dotenv.get_key('.env', 'SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = dotenv.get_key('.env', 'DEBUG')

ALLOWED_HOSTS = [
    dotenv.get_key('.env', 'APP_HOST')
]


# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'importer.apps.ImporterConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'achadosepedidos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'achadosepedidos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'importadorDB.sqlite3'),
    },
    'stage': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': dotenv.get_key('.env', 'DB_HOST_STAGE'),
        'NAME': dotenv.get_key('.env', 'DB_NAME_STAGE'),
        'PORT': dotenv.get_key('.env', 'DB_PORT_STAGE'),
        'USER': dotenv.get_key('.env', 'DB_USER_STAGE'),
        'PASSWORD': dotenv.get_key('.env', 'DB_PASSWORD_STAGE'),
    },
    'production': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': dotenv.get_key('.env', 'DB_HOST'),
        'NAME': dotenv.get_key('.env', 'DB_NAME'),
        'PORT': dotenv.get_key('.env', 'DB_PORT'),
        'USER': dotenv.get_key('.env', 'DB_USER'),
        'PASSWORD': dotenv.get_key('.env', 'DB_PASSWORD'),
    },
}
	
DATABASE_ROUTERS = ['importer.routers.AuthRouter', 'importer.routers.ImporterRoute',]

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

FILE_CHARSET = dotenv.get_key('.env', 'CHARSET')
DEFAULT_CHARSET = dotenv.get_key('.env', 'CHARSET')

LANGUAGE_CODE = dotenv.get_key('.env', 'LANGUAGE_CODE') 

TIME_ZONE = dotenv.get_key('.env', 'TIME_ZONE')

USE_I18N = True

USE_L10N = True

# USE_TZ = True

# Session configutarion
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = os.path.join(BASE_DIR, 'achadosepedidos/tmp')
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_COOKIE_AGE = 43200

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Redirect to home URL after login
LOGIN_REDIRECT_URL = '/importer/index'
LOGIN_URL = '/importer/login'

# Celery configs
BROKER_URL = 'amqp://localhost//'
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'