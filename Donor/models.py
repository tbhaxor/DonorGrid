from django.db import models


# Create your models here.
class Donor(models.Model):
    first_name = models.CharField(max_length=75, null=False, default='Anonymous')
    last_name = models.CharField(max_length=75, null=False, default='Donor')
    email = models.EmailField(null=False, default=None)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name
    pass
