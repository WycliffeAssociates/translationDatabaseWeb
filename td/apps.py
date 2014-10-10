from django.apps import AppConfig as BaseAppConfig
from django.utils.importlib import import_module


class AppConfig(BaseAppConfig):

    name = "td"
    verbose_name = "Translation Database"

    def ready(self):
        import_module("td.receivers")