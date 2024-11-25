from django.db import models

class Player(models.Model):
    normalized_name = models.CharField(max_length=255, unique=True)
    original_name = models.CharField(max_length=255)
    wiki_url = models.URLField()
    full_record = models.TextField()
    age = models.IntegerField(null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    club_career = models.JSONField()
    intl_career = models.JSONField()
    youth_career = models.JSONField(null=True, blank=True)
    managerial_career = models.JSONField(null=True, blank=True)

class DailyGame(models.Model):
    date = models.DateField(unique=True)
    player_pairs = models.JSONField()  # Store the list of player pairs for the day
    precomputed_links = models.JSONField()  # Store the precomputed links for these pairs
    link_types = models.JSONField()  # Store the link types for each pair

    def __str__(self):
        return f"DailyGame for {self.date}"

from django.utils import timezone

class GameSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    current_round = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    lives_remaining = models.IntegerField(default=3)
    start_player = models.CharField(max_length=100)
    end_player = models.CharField(max_length=100)
    link_type = models.CharField(max_length=50)
    intermediate_players = models.JSONField(default=list)
    previous_guesses = models.JSONField(default=list)
    round_scores = models.JSONField(default=list)
    is_game_won = models.BooleanField(default=False)
    round_data = models.JSONField(default=list)
    round_results = models.JSONField(default=list)
    is_game_completed = models.BooleanField(default=False)
    last_played_date = models.DateField(default=timezone.now)  # New field to store the last played date

    def __str__(self):
        return f"Game Session {self.session_id}"
