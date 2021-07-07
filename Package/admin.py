from django.contrib import admin
from .models import Package


# Register your models here.
@admin.register(Package)
class PackageModel(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = ['name', 'amount', 'recurring_unit', 'recurring_interval']
    pass
