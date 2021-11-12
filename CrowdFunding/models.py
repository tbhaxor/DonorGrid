from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


# Create your models here.
class Funding(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")

    name = models.CharField(max_length=128, null=False, blank=False, default=None, help_text='Enter the name for funding campaign',
                            verbose_name='Name')
    description = RichTextField(max_length=256, null=False, blank=False, default=None, verbose_name='Description',
                                help_text='Let donors know more about the campaign')
    target = models.FloatField(validators=[MinValueValidator(1.0, message='Target should be at least 1.0')], null=False, default=1.0, blank=False,
                               help_text='Enter the target amount of the funding')
    status = models.CharField(max_length=25, default=Status.ACTIVE, null=False, blank=False, verbose_name="Current Status",
                              help_text="Current status of the funding. Only active fundings can request for donations from the users",
                              choices=Status.choices)

    class Meta:
        verbose_name = 'Funding'
        verbose_name_plural = 'Fundings'
