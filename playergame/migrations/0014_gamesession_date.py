# Generated by Django 5.0.6 on 2024-09-03 03:06

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playergame', '0013_alter_gamesession_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]