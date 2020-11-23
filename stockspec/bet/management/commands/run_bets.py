from collections import namedtuple

from django.utils import timezone
from django.db.models import Count
from django.core.management.base import BaseCommand

from stockspec.bet.models import Bet


class Command(BaseCommand):
    """Run bets to find who won/lost"""

    def handle(self, *args, **kwargs):
        now = timezone.now()
        bets = (
            Bet.ongoing()
            .prefetch_related("portfolios")
            .prefetch_related("portfolios__tickers")
            .prefetch_related("portfolios__user")
            .filter(end_time__isnull=False, end_time__lte=now)
        )

        PortfolioPerf = namedtuple(
            "PortfolioPerf", ["portfolio", "performance"]
        )

        for bet in bets:
            start_date = bet.start_time
            end_date = bet.end_time
            returns = [
                PortfolioPerf(
                    portfolio, portfolio.return_for_period(start_date, end_date)
                )
                for portfolio in bet.portfolios.all()
            ]

            winningperformance = max(
                returns, key=(lambda portfolioperf: portfolioperf.performance)
            )

            if winningperformance is not None:
                bet.winner = winningperformance.portfolio.user
                print(
                    " / ".join(
                        [
                            "%.4f" % portfolioperf.performance
                            for portfolioperf in returns
                        ]
                    )
                )
                print(winningperformance.portfolio.user.username + " wins")

            bet.save()
