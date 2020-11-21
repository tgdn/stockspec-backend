from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from stockspec.users.views import current_user
from stockspec.bet.views import BetsViewSet
from stockspec.portfolio.views import (
    PortfolioList,
    TickerList,
    TopTickersList,
    PriceSeries,
)

router = DefaultRouter()
router.register(r"bets", BetsViewSet, basename="bets")

urlpatterns = [
    path("auth-token", obtain_auth_token),
    path("users/me", current_user),
    # portfolio
    path("portfolios/", PortfolioList.as_view()),
    path("tickers", TickerList.as_view()),
    path("tickers/top", TopTickersList.as_view()),
    # series
    path("series/<str:symbol>", PriceSeries.as_view()),
    # bets
    path("bets/awaiting", BetsViewSet.as_view({"get": "list"}, awaiting=True)),
    path("bets/all", BetsViewSet.as_view({"get": "list"}, all_bets=True)),
    path(
        "bets/all/awaiting",
        BetsViewSet.as_view({"get": "list"}, all_bets=True, awaiting=True),
    ),
    path("", include(router.urls)),
]
