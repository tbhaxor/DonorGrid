from django.contrib import admin
from .models import PaymentMethod


# Register your models here.
@admin.register(PaymentMethod)
class PaymentMethodRegister(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = ["id", "provider", "client_key"]
    pass
