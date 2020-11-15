from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _

from stockspec.portfolio.models import Portfolio, Ticker, StockPrice

admin.site.register(Portfolio)
admin.site.register(Ticker)
admin.site.register(StockPrice)
