import hashlib

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Recipe


@receiver(pre_save, sender=Recipe)
def generate_short_id(sender, instance, **kwargs):
    if not instance.short_id and instance.id:
        hash_object = hashlib.sha1(str(instance.id).encode())
        instance.short_id = hash_object.hexdigest()[:8] 