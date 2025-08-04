from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

CustomUser = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username=settings.SUPERUSER_NAME).exists():
            CustomUser.objects.create_superuser(
                username=settings.SUPERUSER_USERNAME,
                email=settings.SUPERUSER_EMAIL,
                password=settings.SUPERUSER_PASSWORD
            )
            print("スーパーユーザー作成に成功しました")
