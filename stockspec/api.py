from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from stockspec.users.views import current_user
from stockspec.bet.views import BetList
from stockspec.portfolio.views import PortfolioList, TopTickersList

urlpatterns = [
    path("auth-token", obtain_auth_token),
    path("users/me", current_user),
    path("bets/", BetList.as_view()),
    path("portfolios/", PortfolioList.as_view()),
    path("tickers/top", TopTickersList.as_view()),
]
