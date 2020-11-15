from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from stockspec.users.views import current_user
from stockspec.bet.views import BetList
from stockspec.portfolio.views import PortfolioList, TopTickersList

urlpatterns = [
    path("auth-token", obtain_auth_token),
    path("users/me", current_user),
    # bets
    path("bets/", BetList.as_view()),
    path("bets/awaiting", BetList.as_view(awaiting=True)),
    path("bets/all", BetList.as_view(all_bets=True)),
    path("bets/all/awaiting", BetList.as_view(all_bets=True, awaiting=True)),
    # portfolio
    path("portfolios/", PortfolioList.as_view()),
    path("tickers/top", TopTickersList.as_view()),
]
