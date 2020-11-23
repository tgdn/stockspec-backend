from rest_framework import serializers

from stockspec.bet.models import Bet
from stockspec.portfolio.models import Portfolio, Ticker
from stockspec.portfolio.serializers import PortfolioSerialier
from stockspec.users.serializers import BaseUserSerializer


class BetSerializer(serializers.ModelSerializer):
    users = BaseUserSerializer(read_only=True, many=True)
    winner = BaseUserSerializer(read_only=True)
    portfolios = serializers.SerializerMethodField()

    class Meta:
        model = Bet
        fields = [
            "id",
            "users",
            "amount",
            "duration",
            "winner",
            "portfolios",
            "start_time",
            "end_time",
            "created_at",
        ]

    def get_portfolios(self, obj: Bet):
        """
        A method that returns the serialized portfolios iff:
            - the bet started, and therefore assets can be viewed by all.
            - there is only one opponent, and it is the current user.
        Otherwise it returns null
        """
        portfolio_count = obj.portfolios.count()
        request = self.context.get("request")
        if portfolio_count > 1:
            context = dict(start_date=obj.start_time, end_date=obj.end_time)
            return PortfolioSerialier(
                obj.portfolios, context=context, many=True,
            ).data
        elif (
            hasattr(request, "user")
            and portfolio_count == 1
            and obj.portfolios.first().user.id == request.user.id
        ):
            return PortfolioSerialier(obj.portfolios, many=True).data
        return None


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

