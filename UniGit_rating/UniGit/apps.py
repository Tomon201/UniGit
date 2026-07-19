import os
from django.apps import AppConfig


class UnigitConfig(AppConfig):
    name = 'UniGit'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Импортируем сигналы
        import UniGit.signals

        # Запускаем планировщик только если это основной процесс
        if os.environ.get('RUN_MAIN'):
            from . import updater
            updater.start()