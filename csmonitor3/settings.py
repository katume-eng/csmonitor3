from pathlib import Path
import os
import environ

env = environ.Env()
env.read_env('.env')

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'monitor_app.apps.MonitorAppConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

default_dburl = "sqlite:///" + str(BASE_DIR / "db.sqlite3")

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
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/tmp', 'db.sqlite3'),
    }
}

SUPERUSER_USERNAME = env("DJANGO_SUPERUSER_USERNAME")
SUPERUSER_EMAIL = env("DJANGO_SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = env("DJANGO_SUPERUSER_PASSWORD")

# posgresql's settings
#DATABASES = {
#    'default': {
#        "ENGINE": "django.db.backends.postgresql_psycopg2",
#        "NAME": "name", #ご自身が作成したデータベース名
#        "USER": "user", #ご自身が設定したユーザー名
#        "PASSWORD": "password",#ご自身が設定したパスワード
#        "HOST": "localhost",
#        "PORT": "5432",
#    }
#}

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
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"] # 共通の静的ファイルのURL
STATIC_ROOT = BASE_DIR / "staticfiles"