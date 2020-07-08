"companies app models."
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# Create your models here.


class Company(models.Model):
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="companies"
    )
    name = models.CharField(verbose_name=_("company name"), max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(blank=True, verbose_name=_("Company logo"))
    employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="employees_of_company", blank=True
    )
    customers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="customers_of_company", blank=True
    )

    def __str__(self):
        """string representation of company instances."""
        return self.name

    def save(self, *args, **kwargs):
        """overrides save method. 
        if instance has not slug generate company slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        """meta class for company model."""

        verbose_name = _("Company")
        verbose_name_plural = _("Companies")


class Department(models.Model):
    """
    The model in which the information of the company departments is stored.
    """

    name = models.CharField(max_length=40, verbose_name=_("department Name"))
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, verbose_name=_("department users"),
    )
    company = models.ForeignKey(
        to=Company, on_delete=models.CASCADE, related_name="departments"
    )

    class Meta:
        """meta class for department model."""

        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

    def __str__(self):
        """string representation of department instance."""
        return f"{self.company.name}'s {self.name} department"
