from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from stockspec.portfolio.models import Portfolio, Ticker, StockPrice
from stockspec.portfolio.serializers import (
    PortfolioSerialier,
    TickerSerializer,
    StockPriceSerializer,
)


class PortfolioList(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioSerialier

    def get_queryset(self):
        """return portfolios owned by current user
        """
        user = self.request.user
        return Portfolio.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TopTickersList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TickerSerializer
    queryset = Ticker.top_tickers()


class PriceSeries(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None
    serializer_class = StockPriceSerializer
    lookup_field = "symbol"

    def get_queryset(self):
        """Returns a series of the last 100 prices efficiently
        """
        assert self.lookup_field in self.kwargs, (
            "Expected %s to be called with a URL keyword argument named '%s'."
            % (self.__class__.__name__, self.lookup_field)
        )
        # check symbol
        symbol = self.kwargs[self.lookup_field]
        get_object_or_404(Ticker, symbol=symbol)

        # Efficient limit-offset method for getting last n-rows
        return StockPrice.objects.raw(
            """
            SELECT * FROM price
            WHERE ticker_id = %s
            ORDER BY datetime ASC
            LIMIT 100
            OFFSET (SELECT count(*) FROM price WHERE ticker_id = %s) - 100
            """,
            [symbol, symbol],
        )

