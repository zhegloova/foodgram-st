import hashlib

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Recipe


@receiver(pre_save, sender=Recipe)
def generate_short_id(sender, instance, **kwargs):
    """
    Генерирует короткий идентификатор для рецепта перед сохранением,
    если он еще не существует.
    """
    if not instance.short_id and instance.id:
        # Используем ID рецепта для генерации уникального short_id
        hash_object = hashlib.sha1(str(instance.id).encode())
        instance.short_id = hash_object.hexdigest()[:8] 