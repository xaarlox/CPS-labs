from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


#@receiver(post_save, sender=Profile)
def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        full_name = f"{user.first_name} {user.last_name}".strip()
        profile = Profile.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            name=full_name,
            is_admin=False
            )


def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.first_name = profile.name.split(' ')[0] if profile.name else ''
        user.last_name = ' '.join(profile.name.split(' ')[1:]) if len(profile.name.split(' ')) > 1 else ''
        user.username = profile.username
        user.email = profile.email
        user.save()


def deleteUser(sender, instance, **kwargs):
    user = instance.user
    user.delete()


post_save.connect(createProfile, sender=User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender=Profile)
