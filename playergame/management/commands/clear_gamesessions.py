from django.core.management.base import BaseCommand
from playergame.models import GameSession

class Command(BaseCommand):
    help = 'Clears all data from the GameSession model'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Clearing all data from the GameSession model...'))

        # Delete all GameSession records
        GameSession.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('All data cleared from the GameSession model!'))
