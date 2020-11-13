# Generated by Django 3.1.2 on 2020-11-13 18:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0007_portfolio_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockprice',
            name='ticker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='portfolio.ticker'),
        ),
    ]
