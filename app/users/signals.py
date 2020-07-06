"signals of the users application"
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def create_profile_when_user_approved(sender, instance, created, **kwargs):
    """automatically creates a blank profile when the user account is verified."""
    if instance.is_approved and instance.is_staff:
        Profile.objects.get_or_create(owner=instance)


# @receiver(post_save, StaffInvitation)
# def create_user_when_invitation_confirmed(sender, instance, created, **kwargs):
#     """Automatically create users when the invitation is approved."""
#     if instance.confirmed:
#         UserModel.objects.create_user()
