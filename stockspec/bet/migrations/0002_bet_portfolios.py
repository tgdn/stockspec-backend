# Generated by Django 3.1.2 on 2020-11-13 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_portfolio'),
        ('bet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bet',
            name='portfolios',
            field=models.ManyToManyField(to='portfolio.Portfolio'),
        ),
    ]
