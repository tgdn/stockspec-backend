from django.contrib import admin

from stockspec.portfolio.models import Portfolio, Ticker, StockPrice

admin.site.register(Portfolio)
admin.site.register(Ticker)
admin.site.register(StockPrice)
