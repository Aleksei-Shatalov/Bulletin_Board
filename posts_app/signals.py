from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Author
import logging
from django.contrib.auth.models import Permission

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_author_profile(sender, instance, created, **kwargs):
    if created:
        if not Author.objects.filter(user=instance).exists():
            Author.objects.create(user=instance)
            logger.info(f'Author created for user {instance.username}')

@receiver(post_save, sender=User)
def add_permission_on_user_create(sender, instance, created, **kwargs):
    if created:
        permission = Permission.objects.get(codename='add_image')
        instance.user_permissions.add(permission)