from django.db import models
from Donor.models import Donor
from Package.models import Package


# Create your models here.
class Donation(models.Model):
    donor = models.ForeignKey(to=Donor, on_delete=models.SET_NULL, null=True, default=None)
    package = models.ForeignKey(to=Package, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    pass
