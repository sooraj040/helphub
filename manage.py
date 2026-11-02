#!/usr/bin/env python
"""
Django's command-line tool. You use it to run commands such as:

    python manage.py runserver        start the website on your computer
    python manage.py test accounts    run the automatic checks
    python manage.py migrate          update the database tables
    python manage.py createsuperuser  create an admin account

Django creates this file automatically; it doesn't need changing.
"""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
