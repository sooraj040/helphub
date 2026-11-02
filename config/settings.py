"""
HelpHub settings.

This file is HelpHub's control panel. It tells Django which database
to use, where to find the page templates and stylesheets, which parts
of the site are switched on, and where to send people after they log
in or out.

Private values (like the secret key) are NOT written here. They are
read from a separate file called ".env", which is never shared.
See ".env.example" for the list of values it needs.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# The main HelpHub folder. Other folders are found from here,
# for example BASE_DIR / 'templates' is the "templates" folder.
BASE_DIR = Path(__file__).resolve().parent.parent

# Read the private values from the .env file.
load_dotenv(BASE_DIR / '.env')


# ---------------------------------------------------------------
# Security
# ---------------------------------------------------------------

# A long random password Django uses to protect logins and forms.
# It must be kept secret.
SECRET_KEY = os.environ['SECRET_KEY']

# DEBUG mode shows detailed error pages, which helps while building
# the site. It must be switched OFF on the live website.
# The .env file says "True" or "False".
debug_setting = os.environ.get('DEBUG', 'False')
DEBUG = debug_setting.lower() in ['true', '1', 'yes']

# The web addresses this site is allowed to be opened on.
# The .env file lists them separated by commas, e.g. "127.0.0.1,localhost".
ALLOWED_HOSTS = []
for host in os.environ.get('ALLOWED_HOSTS', '').split(','):
    host = host.strip()
    if host:
        ALLOWED_HOSTS.append(host)


# ---------------------------------------------------------------
# Parts of the site that are switched on
# ---------------------------------------------------------------

INSTALLED_APPS = [
    # Built-in Django features
    'django.contrib.admin',          # the admin site at /admin/
    'django.contrib.auth',           # user accounts, passwords and logins
    'django.contrib.contenttypes',
    'django.contrib.sessions',       # remembers who is logged in
    'django.contrib.messages',       # one-time notices like "Profile updated"
    'django.contrib.staticfiles',    # serves the CSS file

    # HelpHub's own features
    'accounts',                     # sign up, log in, dashboards, profiles
    'services'
]

# Checks that run on every page request, mostly for security.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',   # blocks forged form submissions
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# The file that lists every web address on the site.
ROOT_URLCONF = 'config.urls'

# Where the HTML page templates are kept.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            # Information every page can use, such as the logged-in user.
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Used by the web server when the site is put online.
WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------
# Database (SQLite)
# ---------------------------------------------------------------

# SQLite keeps the whole database in one file, db.sqlite3, in the
# main HelpHub folder. No separate database server or password needed.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------------------------
# Password rules for new accounts
# ---------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    # Not too similar to the username or email
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # At least 8 characters
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # Not a well-known password like "password123"
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # Not only numbers
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ---------------------------------------------------------------
# Language and time
# ---------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------
# Stylesheets and other static files
# ---------------------------------------------------------------

# The web address the CSS is served from, e.g. /static/css/styles.css
STATIC_URL = 'static/'

# The folder where we keep our CSS.
STATICFILES_DIRS = [BASE_DIR / 'static']

# When the site goes online, all static files are copied into this
# folder (with the "collectstatic" command) for the web server.
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ---------------------------------------------------------------
# Logging in and out
# ---------------------------------------------------------------

# Pages that need a login send visitors here first.
LOGIN_URL = 'accounts:login'

# Where people go after logging in.
LOGIN_REDIRECT_URL = 'accounts:dashboard'

# Where people go after logging out.
LOGOUT_REDIRECT_URL = 'accounts:login'
