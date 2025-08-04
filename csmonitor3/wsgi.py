import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csmonitor3.settings')

application = get_wsgi_application()

# WhiteNoise を設定（gzip圧縮やキャッシュ対応も有効に）
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'), prefix='static/')
