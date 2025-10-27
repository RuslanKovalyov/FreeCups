from django.db import IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create Profile when User is created (if not exists)"""
    if created:
        # get_or_create will return existing profile if admin already created it with data
        Profile.objects.get_or_create(user=instance)
