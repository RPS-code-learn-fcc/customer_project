"""
Django settings for customer_project project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# for deployment - import the following:
from environ import Env
env = Env()
Env.read_env()
ENVIRONMENT = env('ENVIRONMENT', default="production")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

ENCRYPT_KEY = env('ENCRYPT_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']

# add for debuggin
INTERNAL_IPS = (
    '127.0.0.1',
    'localhost:8000'
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage', # django cloudinary
    'cloudinary',
    'django.contrib.sites', #django-allauth
    'admin_honeypot',
    'allauth',
    'allauth.account',
    'django_cleanup.apps.CleanupConfig',
    'django_extensions',
    'customers',
    'app_users',
    'django_htmx',
]
SITE_ID = 1
# overrides the default user mdoel & references a custom user model instead
AUTH_USER_MODEL = 'app_users.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", # white noise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    "allauth.account.middleware.AccountMiddleware", # djangoallauth
    

]

ROOT_URLCONF = 'customer_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # needed for: django-allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    
]

# Needed for Django all-auth
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'customer_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# POSTGRES_LOCALLY = False (PostgreSQL is being used remotely), POSTGRES_LOCCALLY = True (local use of PostgreSQL)
POSTGRES_LOCALLY = True
if ENVIRONMENT == "production" or POSTGRES_LOCALLY == True: # if the production value is set -> it is using render.com, else it is using postgreSQL locally, else it is using sql lite in production
    DATABASES['default'] = dj_database_url.parse(env('DATABASE_URL'))

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Directory for additional static files (besides app-level static directories)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# set the default timezone and make sure django is aware of it
TIME_ZONE = 'America/New_York'
USE_TZ = True

# Media files (user uploaded images, documents, etc.)
MEDIA_URL = '/media/'  # URL for accessing media files (e.g., http://example.com/media/)

# cloudinary storage:
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUD_NAME'),
    'API_KEY': env('CLOUD_API_KEY'),
    'API_SECRET': env('CLOUD_API_SECRET')
}

if ENVIRONMENT == "production" or POSTGRES_LOCALLY == True: # checks where postgres is running (locally or through render.com, else it uses the development
    STORAGES = { "default": { "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage", }, 
                "staticfiles": { "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage", },  # for images       
                "raw": { "BACKEND": "cloudinary_storage.storage.RawMediaCloudinaryStorage",  # For raw files (PDFs, etc.)
                }, 
                }
    

else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Directory where uploaded files are stored - absolute filesystem path - in storage

# ---- ADD the following to integrate with Django allauth ------
ACCOUNT_USERNAME_REQUIRED = False

ACCOUNT_EMAIL_REQUIRED = True  # Ensure email is required
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Use email for authentication

ACCOUNT_USER_DISPLAY = lambda user: user.user_name if hasattr(user, 'user_name') else user.email

# Specify a logout and login redirect url for django-allauth
LOGIN_REDIRECT_URL = '/customers/home/'
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_LOGOUT_REDIRECT_URL = "/customers/"
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None 
# sends email to terminal for development purposes
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- implement signup via email -----

ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

ACCOUNT_EMAIL_VERIFICATION = "none"

# Allow login via email verification codes
# ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
# ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# Automatically generate and send login codes


ACCOUNT_RATE_LIMITS = {
    "login_failed": "2/300s",  # Allow 5 failed login attempts every 300 seconds
}

ACCOUNT_EMAIL_VERIFICATION_BY_CODE_TIMEOUT = "900s"
ACCOUNT_SESSION_REMEMBER = False

# inactive users are not redirected when they try to login
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False

# Disable password-related settings
ACCOUNT_PASSWORD_REQUIRED = True

ACCOUNT_USERNAME_BLACKLIST = ['admin', 'accounts', 'profile', 'customer', 'customers', 'customadmin']