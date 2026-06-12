"""
Django settings for travel_show project.
For Railway deployment (MySQL + environment variables).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# 项目根目录 (PythonProject4/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 加载 .env 文件（仅用于本地开发，Railway 上环境变量已由平台注入）
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 本地加载 .env: {env_path}")

# 安全密钥：必须从环境变量获取（Railway 上设置 DJANGO_SECRET_KEY）
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    # 本地开发回退（绝对不能用于生产）
    SECRET_KEY = 'django-insecure-local-dev-only'
    print("⚠️ 警告: 未设置 DJANGO_SECRET_KEY，使用不安全的默认值")

# 调试模式：生产环境必须为 False
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# 允许的主机：从环境变量读取，逗号分隔，默认只允许 localhost
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 数据库配置：使用 Railway 提供的 DATABASE_URL（MySQL），本地回退到 SQLite
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}

# 应用定义
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'attractions',  # 你的应用
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

ROOT_URLCONF = 'travel_show.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'travel_show.wsgi.application'

# 密码验证（保持默认）
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置（生产环境需要收集到 STATIC_ROOT）
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # `collectstatic` 会收集到这里
# 本地静态文件目录（如果存在）
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS = [BASE_DIR / 'static']

# 默认主键类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'