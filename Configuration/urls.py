from django.urls import path
from .views import get_active_payment_methods

app_name = 'configurations'
urlpatterns = [
    path('payment-methods/', get_active_payment_methods, name='payment_methods')
]
