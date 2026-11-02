"""
Connects HelpHub to a web server when the site is put online
(for example on PythonAnywhere). Not used when running on your own
computer with "runserver".

Django creates this file automatically; it doesn't need changing.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
