from rest_framework import serializers

from stockspec.bet.models import Bet
from stockspec.portfolio.models import Portfolio, Ticker
from stockspec.users.serializers import BaseUserSerializer


class BetSerializer(serializers.ModelSerializer):
    users = BaseUserSerializer(read_only=True, many=True)

    class Meta:
        depth = 3
        model = Bet
        fields = [
            "id",
            "users",
            "amount",
            "duration",
            "winner",
            "start_time",
            "end_time",
            "created_at",
        ]


class CreateBetSerializer(serializers.ModelSerializer):
    tickers = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Ticker.objects.all(),
    )

    class Meta:
        model = Bet
        fields = ["amount", "duration", "tickers"]
        extra_kwargs = {
            "amount": {"required": True},
            "duration": {"required": True},
        }

    def validate_tickers(self, value):
        # for now we limit to 3 tickers
        if len(value) != 3:
            raise serializers.ValidationError(
                "You need 3 tickers to create a bet"
            )
        return value

    def save(self):
        return self.instance

