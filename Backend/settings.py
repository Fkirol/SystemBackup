from pathlib import Path
from datetime import timedelta
import dj_database_url
import os,sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY', default='your_secret_key')

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
    'Auth',
    'Databases',
    'Notifications',
    'corsheaders',
    'rest_framework',
    'drf_yasg',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Backend.urls'

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

WSGI_APPLICATION = 'Backend.wsgi.application'
ASGI_APPLICATION = 'Backend.asgi.application'

#REDIS_URL = os.environ.get('REDIS_URL')
#if not REDIS_URL:
#    # Manejar el error: mostrar un mensaje, usar un valor por defecto local, etc.
#    print("Error: REDIS_URL no está definida.  Usando una configuración local por defecto.")
#    REDIS_URL = 'redis://localhost:6379'  # Configuración local por defecto
#
#CHANNEL_LAYERS = {
#  'default': {
#    'BACKEND': 'channels_redis.core.RedisChannelLayer',
#    'CONFIG': {
#      'hosts': [os.environ['REDIS_URL']],   # la URL que pusiste en Render env var
#    },
#  }
#}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
	default='sqlite:///db.sqlite3',
	conn_max_age=600
	)
}


CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['https://bacnekdo.onrender.com']
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 9, 

}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),  # Ajusta el tiempo de vida según sea necesario
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_BEARER_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
if DEBUG:
	STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
	STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND")
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")



#LOGGING = {
 #   'version': 1,
  #  'disable_existing_loggers': False,
   # 'handlers': {
    #    'console': {
     #       'class': 'logging.StreamHandler',
      #  },
#    },
 #   'root': {
 #       'handlers': ['console'],
  #      'level': 'DEBUG',           # o INFO para menos ruido
   # },
    #'loggers': {
     #   # Asegúrate de capturar también errores de Channels y Daphne
      #  'django': {
       #     'handlers': ['console'],
        #    'level': 'DEBUG',
       #     'propagate': True,
       # },
       # 'channels': {
       #     'handlers': ['console'],
       #     'level': 'DEBUG',
       #     'propagate': True,
       # },
       # 'daphne': {
       #     'handlers': ['console'],
       #     'level': 'DEBUG',
       #     'propagate': True,
 #       },
 #   },
#}
