from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Package(models.Model):
    class RecurringInterval(models.TextChoices):
        MONTHLY = 'month', _('Monthly')
        YEARLY = 'year', _('Yearly')
        pass
    name = models.CharField(max_length=20, null=False, default=None, blank=False)
    description = models.TextField(max_length=256, null=False, blank=True, default='')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    recurring_unit = models.IntegerField(validators=[MinValueValidator(1, message='Recurring unit must be greater than 0')], null=True, blank=True,
                                         help_text='Set this if you want to make this package recurring')
    recurring_interval = models.CharField(max_length=10, default=None, blank=True, choices=RecurringInterval.choices, help_text='Set this if you want to make this package recurring')
    currency = models.CharField(max_length=4, default='USD', null=False, blank=True)

    def __str__(self):
        return self.name
    pass