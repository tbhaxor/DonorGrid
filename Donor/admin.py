from django.contrib import admin
from Donor.models import Donor


# Register your models here.
@admin.register(Donor)
class DonorModel(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = ['email', 'first_name', 'last_name']
    pass
