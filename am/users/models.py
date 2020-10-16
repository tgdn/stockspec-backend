import logging

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, blank=False)
    picture_url = models.TextField(_("picture"), blank=True, null=True)
