from pathlib import Path
import os
import environ

env = environ.Env()
env.read_env('.env')

def env_list(key, default=None, sep=","):
    raw = os.environ.get(key)
    if not raw:
        return default or []
    return [s.strip() for s in raw.split(sep) if s.strip()]

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = [h for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

INSTALLED_APPS = [
    "corsheaders",
    'monitor_app.apps.MonitorAppConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',            # ← できるだけ上
    'whitenoise.middleware.WhiteNoiseMiddleware',       # 静的は早めに処理してOK
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS 設定（env から）
CORS_ALLOWED_ORIGINS = env_list("FRONTEND_ORIGINS", default=["http://localhost:3000"])
CORS_ALLOW_CREDENTIALS = os.environ.get("CORS_ALLOW_CREDENTIALS", "False").lower() in ("1","true","yes")

# CSRF trust（POST をブラウザから送る場合に必要）
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", default=[])

ROOT_URLCONF = 'csmonitor3.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # テンプレートディレクトリのパス
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'csmonitor3.wsgi.application'

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='postgres://postgres@localhost:5432/csmonitor_db'
    )
}

SUPERUSER_NAME = env("DJANGO_SUPERUSER_USERNAME")
SUPERUSER_EMAIL = env("DJANGO_SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = env("DJANGO_SUPERUSER_PASSWORD")

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# staticfiles setting
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'