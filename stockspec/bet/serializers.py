from rest_framework import serializers

from stockspec.bet.models import Bet
from stockspec.portfolio.models import Portfolio
from stockspec.users.serializers import BaseUserSerializer


class BetSerializer(serializers.ModelSerializer):
    users = BaseUserSerializer(read_only=True, many=True)

    class Meta:
        depth = 3
        model = Bet
        fields = [
            "users",
            "amount",
            "duration",
            "winner",
            "start_time",
            "end_time",
            "created_at",
        ]

