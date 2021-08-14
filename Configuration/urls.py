from django.urls import path
from .views import get_active_payment_methods, get_custom_fields

app_name = 'configurations'
urlpatterns = [
    path('payment-methods/', get_active_payment_methods, name='payment_methods'),
    path('custom-fields/', get_custom_fields, name='custom_fields')
]
