# Generated by Django 3.1.2 on 2020-11-23 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_auto_20201117_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticker',
            name='delta_change',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='ticker',
            name='last_price',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='ticker',
            name='percentage_change',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
    ]
