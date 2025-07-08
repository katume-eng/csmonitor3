from django.core.management.base import BaseCommand
from monitor_app.models import Collected

class Command(BaseCommand):
    help = 'Collectedモデルの全データを削除します'

    def handle(self, *args, **options):
        count = Collected.objects.count()
        Collected.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Collectedの全データ({count}件)を削除しました'))