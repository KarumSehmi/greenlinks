# Generated by Django 5.0.6 on 2024-09-03 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playergame', '0015_alter_gamesession_session_id_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='gamesession',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='gamesession',
            name='session_id',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.RemoveField(
            model_name='gamesession',
            name='date',
        ),
    ]