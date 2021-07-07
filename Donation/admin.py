from django.contrib import admin
from .models import Donation


# Register your models here.
@admin.register(Donation)
class DonationModel(admin.ModelAdmin):
    list_display = ['donor', 'package', 'amount', 'created_at']
    list_filter = ['created_at']
    sortable_by = ['created_at', 'donor']
    pass
