# Generated by Django 5.0.6 on 2024-09-03 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playergame', '0008_gamesession_round_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='round_results',
            field=models.JSONField(default=list),
        ),
    ]
