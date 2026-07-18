from django.apps import AppConfig


class UnigitConfig(AppConfig):
    name = 'UniGit'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Этот код сработает при запуске сервера
        from . import updater
        updater.start()
