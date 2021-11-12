from django.contrib import admin
from django.db.models.aggregates import Sum
from django.urls.base import reverse
from django.utils.html import mark_safe
from CrowdFunding.models import Funding


# Register your models here.
@admin.register(Funding)
class FundingRegister(admin.ModelAdmin):
    list_display = ('name', 'target', 'status', 'total_donated', 'last_3_donations')

    def total_donated(self, obj: Funding):
        return obj.donations.aggregate(Sum('amount'))['amount__sum'] or 0

    def last_3_donations(self, obj: Funding):
        payload = "<ol>"
        payload += "<style> .recent-donations:hover { text-decoration: underline }</style>"
        donations = obj.donations.order_by("-created_at").all()[:3]
        for donation in donations:
            link = reverse("admin:Donation_donation_change", args=(donation.id,))
            donor_email = donation.donor.email
            amount = donation.amount
            payload += f'<li><a class="recent-donations" href="{link}">{donor_email} : {amount}</a></li>'
            pass
        payload += "</ol>"
        return mark_safe(payload)

    pass
