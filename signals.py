from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import Issue, Document
import os

@receiver(post_delete, sender=Document)
def document_delete_handler(sender, **kwargs):
    default_storage.delete(kwargs.get('instance').file.name)

@receiver(post_delete, sender=Issue)
def issue_delete_handler(sender, **kwargs):
    """removes issue filestorage subdirectory and files"""
    #default_storage.delete(kwargs.get('instance').file.name)
    id=kwargs.get('instance').id
    p=os.path.join(default_storage.location)
