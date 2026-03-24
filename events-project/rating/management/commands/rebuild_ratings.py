from django.core.management.base import BaseCommand

from rating.services import rebuild_leaderboard


class Command(BaseCommand):
    help = 'Пересчитать рейтинг всех участников и обновить ранги'

    def handle(self, *args, **options):
        self.stdout.write('Пересчёт рейтингов...')
        rebuild_leaderboard()
        self.stdout.write(self.style.SUCCESS('Готово.'))
