from rest_framework import serializers

from stockspec.bet.models import Bet


class BetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = [
            "portfolios",
            "amount",
            "duration",
            "winner",
            "start_time",
            "end_time",
            "created_at",
        ]

