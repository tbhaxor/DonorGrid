from django.conf import settings
from django.apps import AppConfig
from urllib.parse import urlparse
import sys


class ConfigurationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Configuration'
