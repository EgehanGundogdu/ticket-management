import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampMixin(models.Model):
    """timestamp mixin for tickets app models."""

    created = models.DateTimeField(
        verbose_name=_("Create date "), auto_now_add=True, db_index=True
    )
    updated = models.DateTimeField(verbose_name=_("Update date"), auto_now=True)

    class Meta:
        """abstract definition for mixin."""

        abstract = True


class Activity(models.Model):
    """activity model for actions on system."""

    ACTIONS = (
        ("C", _("commented")),
        ("L", _("locked")),
        ("U", _("unlocked")),
        ("O", _("opened")),
        ("UP", _("updated")),
        ("AT", _("attached")),
    )

    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_("Owner of activity"),
        on_delete=models.CASCADE,
    )
    action = models.CharField(
        verbose_name=_("action type"), choices=ACTIONS, max_length=20
    )
    created = models.DateTimeField(
        verbose_name=_("create date"), auto_now_add=True, db_index=True
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")


def get_ticket_identifer() -> str:
    """
    Unique short identifier generator for tickets.
    For example 53d55e54
    """
    return uuid.uuid4().hex[:8]


class Ticket(TimeStampMixin):

    """"ticket model. inherit from time stamp mixin."""

    PRIORTY = ((1, _("Low")), (2, _("Normal")), (3, _("High")), (4, _("Critical")))

    owner = models.ForeignKey(
        verbose_name=_("Ticket owner"),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    related_user = models.ForeignKey(
        verbose_name=_("Attached user"),
        to=settings.AUTH_USER_MODEL,
        related_name="attached_tickets",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    company = models.ForeignKey(
        to="companies.Company",
        verbose_name=_("Company"),
        related_name="tickets",
        on_delete=models.CASCADE,
    )
    department = models.ForeignKey(
        verbose_name=_("Ticket department"),
        to="companies.Department",
        on_delete=models.SET_NULL,
        related_name="tickets",
        null=True,
    )
    header = models.CharField(verbose_name=_("Header"), max_length=200)
    content = models.TextField(verbose_name=_("Content"))
    identifier = models.CharField(
        verbose_name=_("Ticket unique identifier"),
        default=get_ticket_identifer,
        unique=True,
        max_length=12,
    )
    status = models.BooleanField(default=True, verbose_name=_("Status"))
    priorty = models.IntegerField(
        verbose_name=_("Priorty"), choices=PRIORTY, default=PRIORTY[0][0]
    )
    activities = GenericRelation(Activity)

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        return f"ticket {self.identifier} owner: {self.user.get_full_name()}"


class TicketComment(TimeStampMixin):
    """Ticket commnet model with timestamp mixin."""

    owner = models.ForeignKey(
        verbose_name=_("Comment owner"),
        to=settings.AUTH_USER_MODEL,
        related_name="owned_ticket_comments",
        on_delete=models.CASCADE,
    )
    ticket = models.ForeignKey(
        verbose_name=_("Ticket"),
        on_delete=models.CASCADE,
        related_name="ticket_comments",
        to="tickets.Ticket",
    )
    content = models.TextField(verbose_name=_("Comment content"))

    def __str__(self):
        """string representation of ticket comment model."""
        return f"{self.ticket.identifier}'s comment"
