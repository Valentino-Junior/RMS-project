import os
from pathlib import Path
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

IMPORT_EXPORT_USE_TRANSACTIONS = True
# Define BASE_DIR before using it
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables from the .env file
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Configure Sentry
import sentry_sdk

sentry_sdk.init(
    dsn="https://3078e06f1831779a26dce799dd79aca7@o4508409447317504.ingest.us.sentry.io/4508409449021440",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
SITE_NAME = 'rms.com'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://prompt-firstly-dassie.ngrok-free.app', #chnage this port and replace with the one ur runnin
    'http://127.0.0.1:8000',
    'http://localhost:8000'
]


SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.contrib.sessions': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Installed apps
INSTALLED_APPS = [
    'jazzmin',
    'compressor',
    'django.contrib.admin',
    'machineLearning',
    'website',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'easyaudit',
    'import_export',
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
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
]

ROOT_URLCONF = 'Company.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'Company.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465)) 
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL") == 'True' 
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER") 
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD") 
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)  
EMAIL_SUBJECT_PREFIX = os.getenv("EMAIL_SUBJECT_PREFIX", '[RMS.COM]')
EMAIL_USE_TLS = False  

SITE_URL = env('SITE_URL')

# Authentication settings
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Default backend for username
    'website.authentication.EmailOrUsernameBackend',  # Path to the custom backend
)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LOGIN_URL = '/account/signin/'
LOGIN_REDIRECT_URL = '/account/profile/'



BASE_DIR = Path(__file__).resolve().parent.parent

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'  
STATIC_URL = '/static/'  
MEDIA_URL = '/media/'  

STATIC_ROOT = os.path.join(BASE_DIR, 'assets')  # Used in production to collect static files  
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')         # Used for storing uploaded media files  

if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # Use 'static' for development  
else:
    STATICFILES_DIRS = []  # Not needed in production

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JAZZMIN_SETTINGS = {
    "site_title": "RMS",
    "site_header": "RMS",
    "site_brand": "RMS",
    "site_logo": '/img/rms.png',
    "welcome_sign": "Welcome to the RMS PORTAL",
    "copyright": "RMS",
    "search_model": [],
    "custom_css": None,
    "hide_version": True,
    "hide_footer": True,
    "show_ui_builder": False,
    "topmenu_links": [],
    "icons": {
        # Django built-in models
        "auth.User": "fa fa-user",  # Icon for User model
        "auth.Group": "fa fa-users",  # Icon for Group model
        # Add icons for the `website` app models
        "website.website": "fa fa-home",         # Website model
        "website.section1": "fa fa-home",        # Section1 model
        "website.section2": "fa fa-home",        # Section2 model
        "website.section2header": "fa fa-home",  # Section2Header model
        "website.section3": "fa fa-home",        # Section3 model
        "website.section3header": "fa fa-home",  # Section3Header model
        "website.section4": "fa fa-home",        # Section4 model
        "website.section5": "fa fa-home",        # Section5 model
        "website.section6": "fa fa-home",        # Section6 model
        "website.section_6_image": "fa fa-home", # Section_6_Image model
        "website.section7": "fa fa-home",        # Section7 model
        "website.section8": "fa fa-home",        # Section8 model
        "website.section9": "fa fa-home",        # Section9 model
        "website.section9title": "fa fa-home",   # Section9Title model
        "website.section10": "fa fa-home",       # Section10 model
        "website.section11": "fa fa-home",       # Section11 model
        "website.section13": "fa fa-street-view",       # Section13 model
        "website.subscription": "fa fa-mouse-pointer",    # Subscription model
        "website.messages": "fa fa-comment",        # Messages model
        "website.groupusers": "fa fa-users", # Easyaudit models
        "website.Email": "fa fa-envelope",
        "website.ForgotPassword": "fa fa-key",
        "website.Notification": "fa fa-bell",
        "website.ProfilePicture": "fa fa-camera",
        "website.Profile": "fa fa-user-circle",
        "website.About": "fa fa-info-circle",
        "easyaudit.CRUDEvent": "fa fa-cogs",
        "easyaudit.LoginEvent": "fa fa-sign-in-alt",
        "easyaudit.RequestEvent": "fa fa-paper-plane",     },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-success",
    "navbar": "navbar-success navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "journal",
    "dark_mode_theme": "cyborg",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "hide_version": True,
    "hide_footer": True,
    "show_ui_builder": False
}