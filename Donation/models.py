from django.db import models
from Donor.models import Donor
from Package.models import Package
from Configuration.models import PaymentMethod


# Create your models here.
class Donation(models.Model):
    donor = models.ForeignKey(to=Donor, on_delete=models.SET_NULL, null=True, default=None)
    package = models.ForeignKey(to=Package, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    currency = models.CharField(max_length=3, default='USD', null=False, blank=True)
    txn_id = models.CharField(max_length=255, null=True, blank=False)
    provider = models.CharField(max_length=15, choices=PaymentMethod.PaymentProvider.choices, default=PaymentMethod.PaymentProvider.STRIPE)
    pass
