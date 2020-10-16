import sys
import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User as IUser
from django.contrib.auth import get_user_model
from django.conf import settings

User: IUser = get_user_model()


class Command(BaseCommand):
    help = "Creates initial admin user"

    def handle(self, *args, **kwargs):
        if User.objects.filter(username="thomas").exists():
            logging.info("admin exists")
        else:
            User.objects.create_superuser(
                "thomas", "tgdn45@gmail.com", "thomas"
            )
            logging.info("admin created")
        sys.exit()
