"""
Django settings for cheapies project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from django.conf import settings
from django.conf.urls.static import static

MEDIA_ROOT = os.path.abspath('cheapiesgr/static')
MEDIA_URL = '/media/'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vaary-tka#uea+lwiijfm)as*hr@@fs2t-&w^&=e+1=(4=@#z&'

# HTTPS/SSL
SECURE_SSL_REDIRECT = False

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cheapiesgr',
    'api',
    'social_django',
    'django.contrib.gis',
    'djgeojson',
    'el_pagination',
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
    'sslserver'
]

# AUTH_USER_MODEL = 'cheapiesgr.Volunteer'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'cheapies.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                ],
        },
    },
]

WSGI_APPLICATION = 'cheapies.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': './database.cnf',
            'unix_socket': '/var/run/mysqld/mysqld.sock'
        },

    }
}

# Password Hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'el'

USE_I18N = True

USE_L10N = True

TIME_ZONE = 'Europe/Athens'

USE_I18N = True

USE_L10N = True

USE_TZ = True

GRAPH_MODELS = {
          'all_applications': True,
            'group_models': True}

STATIC_URL = '/static/'

# AUTHENTICATION_BACKENDS = (
#
#     ''' Google Authentication '''
#
#     'social_core.backends.open_id.OpenIdAuth',
#     'social_core.backends.google.GoogleOpenId',
#     'social_core.backends.google.GoogleOAuth2',
#
#     ''' Facebook Authentication '''
#
#     'social_core.backends.facebook.FacebookOAuth2',
#
#     'django.contrib.auth.backends.ModelBackend',
# )

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

# GeoIP2 configuration

GEOIP_PATH = os.path.join(BASE_DIR, 'etc/GeoLite_Archive')


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ]
}
