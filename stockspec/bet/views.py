from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied

from stockspec.bet.models import Bet
from stockspec.bet.serializers import BetSerializer, CreateBetSerializer


class BetsViewSet(ModelViewSet):
    # some filtering params passed to .as_view(**kwargs)
    all_bets = False  # not only the current user's
    awaiting = False  # awaiting an opponent
    previous = False  # finished

    permission_classes = [IsAuthenticated]
    serializer_class = BetSerializer

    def update(self, request, *args, **kwargs):
        raise PermissionDenied()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBetSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """return bets owned by current user or all
        """

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

