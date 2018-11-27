from django.apps import AppConfig


class Config(AppConfig):
    name = 'datamart_notifier'
    verbose_name = 'Datamart Notification Subsystem'

    def ready(self):
        from .monitor import monitor
        monitor.install()
