from django.db import models
from django.db.models import Count

from stockspec.users.models import User
from stockspec.portfolio.models import Portfolio


class Bet(models.Model):
    class Meta:
        db_table = "bet"

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

    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        usernames = self.portfolios.values_list("user__username", flat=True)[:2]
        return ":".join(usernames)

    @staticmethod
    def awaiting():
        return (
            Bet.objects.all()
            .annotate(count=Count("portfolios"))
            .filter(count__lt=2)
        )

    @staticmethod
    def not_finished():
        return Bet.objects.filter(winner__isnull=True)

    @staticmethod
    def finished():
        return Bet.objects.filter(winner__isnull=False)
