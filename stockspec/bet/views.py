from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from stockspec.bet.models import Bet
from stockspec.bet.serializers import BetSerializer


class BetList(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BetSerializer

    def get_queryset(self):
        """return bets owned by current user
        """
        user = self.request.user
        return Bet.objects.filter(portfolios__user=user)
