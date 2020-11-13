from django.db import models
from django.db.models import CheckConstraint, Q, F

from stockspec.users.models import User
from stockspec.portfolio.models import Portfolio


class Bet(models.Model):
    class Meta:
        db_table = "bet"
        # check constraint that portfolio1_id < portfolio2_id
        constraints = [
            CheckConstraint(
                check=Q(portfolio1__lt=F("portfolio2")),
                name="check_portfolio_ids",
            )
        ]

    # for now 5, 10, 15
    FIVE = 5
    TEN = 10
    FIFTEEN = 15
    AMOUNT_CHOICES = [(FIVE, "5"), (TEN, "10"), (FIFTEEN, "15")]

    # 1 day or 1 week (5 days)
    ONEDAY = "1D"
    ONEWEEK = "1W"
    DURATION_CHOICES = [(ONEDAY, "1 day"), (ONEWEEK, "1 week")]

    portfolio1 = models.ForeignKey(
        Portfolio, null=True, on_delete=models.SET_NULL, related_name="bet1",
    )
    portfolio2 = models.ForeignKey(
        Portfolio, null=True, on_delete=models.SET_NULL, related_name="bet2",
    )

    # keep it simple, use an int
    amount = models.IntegerField(choices=AMOUNT_CHOICES, default=FIVE)
    duration = models.CharField(
        max_length=2, choices=DURATION_CHOICES, default=ONEDAY
    )

    # default is null
    winner = models.ForeignKey(
        User, default=None, null=True, on_delete=models.SET_NULL
    )

    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

