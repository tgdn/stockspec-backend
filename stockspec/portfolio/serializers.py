from rest_framework import serializers

from stockspec.users.serializers import BaseUserSerializer
from stockspec.portfolio.models import Portfolio, Ticker, StockPrice


class PortfolioSerialier(serializers.ModelSerializer):
    tickers = serializers.SerializerMethodField()
    perf = serializers.SerializerMethodField()
    user = BaseUserSerializer()

    class Meta:
        model = Portfolio
        fields = ["user", "tickers", "created_at", "perf", "updated_at"]
        read_only_fields = ["user", "perf"]

    def get_perf(self, obj: Portfolio):
        if hasattr(self, "context"):
            start_date = self.context.get("start_date")
            end_date = self.context.get("end_date")

            if all([start_date, end_date]):
                return obj.return_for_period(start_date, end_date)
        return None

    def get_tickers(self, obj: Portfolio):
        if self.context.get("with_tickers", False):
            return TickerSerializer(
                obj.tickers, context=self.context, many=True
            ).data
        return None


class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticker
        fields = [
            "symbol",
            "timezone",
            "company",
            "description",
            "exchange",
            "country",
            "sector",
            "industry",
            "beta",
            "logo_url",
            "last_price",
            "delta",
            "percentage_change",
        ]


class StockPriceSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField(source="close_price")
    time = serializers.ReadOnlyField(source="date")

    class Meta:
        model = StockPrice
        fields = ["price", "time", "volume"]

