from django.utils import timezone
from django.db import models
from django.db.models import Q, Count, Subquery

from stockspec.users.models import User
from stockspec.portfolio.models import Portfolio


class Bet(models.Model):
    class Meta:
        db_table = "bet"
        ordering = ["-created_at"]

    # for now 5, 10, 15
    FIVE = 5
    TEN = 10
    FIFTEEN = 15
    AMOUNT_CHOICES = [(FIVE, "5"), (TEN, "10"), (FIFTEEN, "15")]

    # 1 day or 1 week (5 days)
    ONEDAY = "1D"
    ONEWEEK = "1W"
    DURATION_CHOICES = [(ONEDAY, "1 day"), (ONEWEEK, "1 week")]

    portfolios = models.ManyToManyField(Portfolio)

    # keep it simple, use an int
    amount = models.IntegerField(choices=AMOUNT_CHOICES, default=FIVE)
    duration = models.CharField(
        max_length=2, choices=DURATION_CHOICES, default=ONEDAY
    )

    # default is null
    winner = models.ForeignKey(
        User, default=None, blank=True, null=True, on_delete=models.SET_NULL
    )

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        usernames = self.portfolios.values_list("user__username", flat=True)[:2]
        return ":".join(usernames)

    @property
    def users(self):
        user_ids = self.portfolios.values_list("user", flat=True)
        return User.objects.filter(id__in=Subquery(user_ids[:2]))

    @staticmethod
    def ongoing():
        """Bets not finished yet"""
        return (
            Bet.objects.all()
            .annotate(portfolio_count=Count("portfolios"))
            .filter(
                Q(portfolio_count=2)
                & (Q(winner__isnull=True) | Q(end_time__gte=timezone.now()))
            )
        )

    @staticmethod
    def awaiting():
        """Bets awaiting an opponent"""
        return (
            Bet.objects.all()
            .annotate(portfolio_count=Count("portfolios"))
            .filter(portfolio_count__lt=2)
        )

    @staticmethod
    def not_finished():
        return Bet.objects.filter(winner__isnull=True)

    @staticmethod
    def finished():
        return Bet.objects.filter(winner__isnull=False)
