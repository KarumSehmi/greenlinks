# Generated by Django 5.0.6 on 2024-09-03 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playergame', '0009_gamesession_round_results'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamesession',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='gamesession',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='gamesession',
            name='is_game_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gamesession',
            name='link_type',
            field=models.CharField(max_length=50),
        ),
    ]
