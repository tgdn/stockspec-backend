"""
WSGI config for stockspec project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockspec.settings")

application = get_wsgi_application()

# create initial superuser
os.system("python manage.py bootstrap_user")
# migrate on startup
os.system("python manage.py migrate")
