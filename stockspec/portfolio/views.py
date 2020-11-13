from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from stockspec.portfolio.models import Portfolio, Ticker
from stockspec.portfolio.serializers import PortfolioSerialier, TickerSerializer


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
