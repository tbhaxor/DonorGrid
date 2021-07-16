from django.contrib import admin
from .models import Donation


# Register your models here.
@admin.register(Donation)
class DonationModel(admin.ModelAdmin):
    list_display = ['donor', 'package', 'amount', 'is_completed', 'transaction_id', 'created_at']
    list_filter = ['created_at']
    sortable_by = ['created_at', 'donor']

    @admin.display()
    def transaction_id(self, obj: Donation):
        return obj.txn_id
    pass
