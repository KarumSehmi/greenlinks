# Generated by Django 5.0.6 on 2024-09-03 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playergame', '0011_gamesession_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesession',
            name='session_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='gamesession',
            unique_together={('session_id', 'date')},
        ),
    ]