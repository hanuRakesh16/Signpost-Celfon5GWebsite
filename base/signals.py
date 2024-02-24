from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import *

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        CustomProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.customprofile.save()


@receiver(post_save, sender=CustomProfile)
def change_listing_type(sender, instance, **kwargs):
    username = User.objects.get(username=instance)
    user = CustomProfile.objects.get(user=username)
    if user.account_type == "Premium":
        listings = Task.objects.filter(listing_owner=username)
        if listings:
            for listing in listings:
                listing.listing_type = "Premium"
                listing.save()
                
