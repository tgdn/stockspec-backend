"""
ASGI config for am project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "am.settings")

application = get_asgi_application()

# create initial superuser
os.system("python manage.py bootstrap_user")
# migrate on startup
os.system("python manage.py migrate")
