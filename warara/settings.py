import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# Django settings for warara project.
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

from etc.warara_settings import DEBUG, ADMINS

TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ':memory:'     # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# EMAIL SETTINGS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Seoul'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# Now it is deprecated since django 1.4
# ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm+k6a(t0&&3z6aiej1!7g@c4yrp=!d*=x241s+i4_6($yopp=%'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',  # (pipoket): Django provided automatic caching middleware
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # (pipoket): Django provided automatic caching middleware
)

ROOT_URLCONF = 'warara.urls'

TEMPLATE_DIRS = (
    # Put strings here, like /home/html/django_templates or C:/www/django/templates.
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
        'warara.account',
        'warara.blacklist',
        'warara.board',
        'warara.collection',
        'warara.main',
        'warara.message',
        'warara.mobile',
        'warara.sysop',
        'compressor'
)

COMPRESS = True

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

try:
    from etc.warara_settings import SET_SESSION_FILE_PATH
except ImportError:
    SET_SESSION_FILE_PATH = True

if SET_SESSION_FILE_PATH:
    import tempfile
    #login = os.getlogin()
    login = os.getenv('USER')
    if login == None:
        login = 'www-data'
    temp_dir = tempfile.gettempdir()
    session_dir = os.path.join(temp_dir, 'warara-' + login)
    #session_dir = os.path.join(temp_dir, 'warara')
    if not os.path.exists(session_dir):
        os.mkdir(session_dir)
    SESSION_FILE_PATH = session_dir

try:
    from etc.warara_settings import CACHE_BACKEND, CACHE_MIDDLEWARE_SECONDS
except ImportError:
    pass
