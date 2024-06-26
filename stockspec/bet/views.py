import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from stockspec.bet.models import Bet
from stockspec.bet.serializers import (
    BetSerializer,
    CreateBetSerializer,
    JoinBetSerializer,
)

logger = logging.getLogger(__name__)


class BetsViewSet(ModelViewSet):
    # some filtering params passed to .as_view(**kwargs)
    all_bets = False  # not only the current user's
    awaiting = False  # awaiting an opponent
    previous = False  # finished

    permission_classes = [IsAuthenticated]
    serializer_class = BetSerializer

    def update(self, request, *args, **kwargs):
        raise PermissionDenied()

    def create(self, request, *args, **kwargs):
        """
        Logically the same code as the parent,
        but with a different output serializer.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        outserizalizer = self.serializer_class(
            instance=serializer.instance, context=self.get_serializer_context()
        )
        return Response(outserizalizer.data, status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def join(self, request, *args, **kwargs):
        """
        Join a bet awaiting for opponent.
        We check that there is only one opponent,
        validate the posted data and start the bet.
        """
        # NOTE: we need to avoid race conditions.
        # These will set the valid queryset to use: awaiting bets
        self.all_bets = True
        self.awaiting = True
        bet: Bet = self.get_object()

        if bet.portfolios.first().user == request.user:
            # cannot join your own bet
            raise PermissionDenied
        serializer = self.get_serializer(bet, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        outserizalizer = self.serializer_class(
            instance=serializer.instance, context=self.get_serializer_context()
        )
        return Response(outserizalizer.data, status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBetSerializer
        elif self.action == "join":
            return JoinBetSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """return bets owned by current user or all
        """

        if self.action == "retrieve":
            return Bet.objects.prefetch_related("portfolios").all()

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

