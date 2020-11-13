from rest_framework import serializers

from stockspec.portfolio.models import Portfolio, Ticker


class PortfolioSerialier(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ["user", "tickers", "created_at", "updated_at"]
        read_only_fields = ["user"]


class TickerSerializer(serializers.ModelSerializer):
    latest_price = serializers.ReadOnlyField()

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
            "latest_price",
        ]

