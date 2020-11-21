from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from stockspec.bet.models import Bet
from stockspec.bet.serializers import BetSerializer


class BetsViewSet(ModelViewSet):
    # some filtering params passed to .as_view(**kwargs)
    all_bets = False  # not only the current user's
    awaiting = False  # awaiting an opponent
    previous = False  # finished

    permission_classes = [IsAuthenticated]
    serializer_class = BetSerializer

    def get_queryset(self):
        """return bets owned by current user or all
        """
        print(self.all_bets)
        print(self.action)

        # by default we return user's current bets
        user = self.request.user
        queryset = (
            Bet.objects.all()
            if self.all_bets
            else Bet.objects.filter(portfolios__user=user)
        )
        # django please join
        queryset.prefetch_related("portfolio")
        queryset.select_related("portfolio__user")

        if self.awaiting:
            return Bet.awaiting() & queryset
        elif self.previous:
            return Bet.finished() & queryset

        if self.all_bets:
            return Bet.ongoing()
        return Bet.not_finished() & queryset

