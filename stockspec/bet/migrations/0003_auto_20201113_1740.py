# Generated by Django 3.1.2 on 2020-11-13 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bet', '0002_bet_portfolios'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='bet',
            name='check_portfolio_ids',
        ),
        migrations.RemoveField(
            model_name='bet',
            name='portfolio1',
        ),
        migrations.RemoveField(
            model_name='bet',
            name='portfolio2',
        ),
    ]
