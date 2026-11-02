"""
An alternative way to connect HelpHub to a web server, used by some
hosts. HelpHub currently uses wsgi.py instead.

Django creates this file automatically; it doesn't need changing.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
