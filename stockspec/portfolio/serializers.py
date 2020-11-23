from rest_framework import serializers

from stockspec.portfolio.models import Portfolio, Ticker, StockPrice


class PortfolioSerialier(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ["user", "tickers", "created_at", "updated_at"]
        read_only_fields = ["user"]


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

