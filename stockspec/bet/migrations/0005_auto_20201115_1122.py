# Generated by Django 3.1.2 on 2020-11-15 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bet', '0004_auto_20201115_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bet',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bet',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
