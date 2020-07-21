"users app models."

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    "a model manager of the custom user model. no username field "
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creater method of user model.
        """
        if email is None:
            raise ValueError("Email must be set!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Creater method of normal user.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_company_admin", False)
        return self._create_user(email, password, **extra_fields)

    def create_inactive_user(self, email, password=None, **extra_fields):
        "creater method of inactive user."
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_company_admin", False)
        extra_fields.setdefault("is_active", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creater method of superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_company_admin", False)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Super user must have is_superuser=True flag.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Super user must have is_staff=True flag.")

        return self._create_user(email, password, **extra_fields)

    def create_staff_user(self, email, password=None, **extra_fields):
        """
        Creater method of staff user.
        """
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_company_admin", False)
        return self._create_user(email, password, **extra_fields)

    def create_company_admin(self, email, password=None, **extra_fields):
        "creater method of company admin"
        extra_fields.setdefault("is_company_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):

    """This model override django auth model. this model does not contain a username field."""

    username = None
    first_name = models.CharField(_("first name"), max_length=30)
    last_name = models.CharField(_("last name"), max_length=30)
    email = models.EmailField(_("email address"), unique=True)
    is_company_admin = models.BooleanField(
        verbose_name=_("Company admin"), default=False
    )
    is_approved = models.BooleanField(_("account approve status"), default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()


class Profile(models.Model):
    """model that keeps profile information
    of company employees and officials."""

    owner = models.OneToOneField(
        to=User, on_delete=models.CASCADE, verbose_name=_("owner of profile")
    )
    picture = models.ImageField(verbose_name=_("profile image"), blank=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


class Invitation(models.Model):
    "model that hosts user invitations to the system."
    inviter = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name=_("creater of invitation"),
    )
    first_name = models.CharField(verbose_name=_("invited first name"), max_length=40)
    last_name = models.CharField(verbose_name=_("invited last name"), max_length=40)
    email = models.EmailField(verbose_name=_("invited user email"), unique=True)
    token = models.CharField(
        verbose_name=_("invite token"), editable=False, max_length=255
    )
    uuid = models.UUIDField(
        verbose_name=_("unique uuid identifier"), default=uuid.uuid4
    )
    created = models.DateTimeField(_("invitation created datetime"), auto_now_add=True)
    confirmed = models.BooleanField(
        verbose_name=_("invite confirm status"), default=False
    )
    is_staff = models.BooleanField(_("is staff"))

    def __str__(self):
        "string representation of invitation model instances. returns uuid first 8 char and token"
        return f"{str(self.uuid)[0:8]} - {self.token}"
