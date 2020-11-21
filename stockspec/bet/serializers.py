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
        # for now we limit to 3 tickers, this might change in the future
        if len(value) != 3:
            raise serializers.ValidationError(
                "You need 3 tickers to create a bet"
            )

        return value

    def create(self, validated_data):
        """Create a new bet.
        Checks whether a portfolio with given tickers exists,
        otherwise it creates one, and uses it for this bet.
        """
        request = self.context.get("request")
        if request is None:
            raise Exception("Request context is required")

        user = request.user
        tickers = validated_data.pop("tickers")
        # Avoid recreating a portfolio which contains the same tickers.
        portfolio = Portfolio.exact_tickers(tickers).filter(user=user).first()
        if portfolio is None:
            portfolio = Portfolio.objects.create(user=user)
            portfolio.tickers.set(tickers)

        ModelClass = self.Meta.model
        instance = ModelClass.objects.create(**validated_data)
        instance.portfolios.set([portfolio])
        return instance

