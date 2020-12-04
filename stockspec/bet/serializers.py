from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from stockspec.exceptions import SerializerRequestMissing
from stockspec.bet.models import Bet
from stockspec.portfolio.models import Portfolio, Ticker
from stockspec.portfolio.serializers import PortfolioSerialier
from stockspec.users.serializers import BaseUserSerializer


class BetSerializer(serializers.ModelSerializer):
    winner = BaseUserSerializer(read_only=True)
    portfolios = serializers.SerializerMethodField()

    class Meta:
        model = Bet
        fields = [
            "id",
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
        Disclaimer:
            By default, if bet hasnt started, portfolios should be kept private.

        This method returns the serialized portfolios and includes or not
        the tickers of those portfolios. Tickers are returned iff:
            - the bet started, and therefore assets can be viewed by all.
            - there is only one opponent, and it is the current user.
        Otherwise the portfolio will be returned but its assets will be hidden/null.

        In addition to this, the method lets the portfolio serializer
        calculate the performance of the portfolio if the bet started.
        """

        request = self.context.get("request")
        if request is None:
            raise SerializerRequestMissing

        user = request.user
        portfolio_count = obj.portfolios.count()
        is_awaiting = portfolio_count == 1
        is_full = portfolio_count == 2
        with_tickers = False

        # is it the current and only user in the bet?
        if is_awaiting and obj.portfolios.first().user.id == user.id:
            with_tickers = True
        # the bet has already started?
        elif all([is_full, bool(obj.start_time), bool(obj.end_time)]):
            with_tickers = True

        context = {
            **self.context,
            "with_tickers": with_tickers,
            "start_date": obj.start_time,
            "end_date": obj.end_time,
        }
        return PortfolioSerialier(
            obj.portfolios.all(), context=context, many=True
        ).data


def validate_tickers(tickers):
    """Raise if ticker count != 3"""
    # for now we limit to 3 tickers, this might change in the future
    if len(tickers) != 3:
        raise serializers.ValidationError("You need 3 tickers to create a bet")
    return tickers


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
        return validate_tickers(value)

    def create(self, validated_data):
        """Create a new bet.
        Checks whether a portfolio with given tickers exists,
        otherwise it creates one, and uses it for this bet.
        """
        request = self.context.get("request")
        if request is None:
            raise SerializerRequestMissing

        user = request.user
        tickers = validated_data.pop("tickers")
        # get portfolio and create bet with it
        portfolio = Portfolio.get_or_create_from_tickers(user, tickers)
        ModelClass = self.Meta.model
        instance = ModelClass.objects.create(**validated_data)
        instance.portfolios.set([portfolio])
        return instance


class JoinBetSerializer(serializers.ModelSerializer):
    tickers = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Ticker.objects.all(),
    )

    class Meta:
        model = Bet
        fields = ["tickers"]

    def validate_tickers(self, value):
        return validate_tickers(value)

    def update(self, instance: Bet, validated_data):
        request = self.context.get("request")
        if request is None:
            raise SerializerRequestMissing

        user = request.user
        tickers = validate_tickers.pop("tickers")
        # get and set portfolio
        portfolio = Portfolio.get_or_create_from_tickers(user, tickers)
        instance.portfolios.add(portfolio)

        # now we need to start bet (start_time, end_time)
        deltas = {
            Bet.ONEDAY: timedelta(days=1),
            Bet.ONEWEEK: timedelta(weeks=1),
        }

        now = timezone.now()
        instance.start_time = now
        instance.end_time = now + deltas[instance.duration]
        instance.save()

        return instance
