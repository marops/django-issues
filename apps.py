from django.apps import AppConfig
from django.dispatch import receiver
from django.db.models.signals import post_delete

class IssuesConfig(AppConfig):
    name = 'issues'

    def ready(self):
        from . import signals