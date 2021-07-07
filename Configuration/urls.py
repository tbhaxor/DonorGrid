from django.urls import path
from .views import AllPaymentMethods

app_name = 'configurations'
urlpatterns = [
    path('payment-methods/', AllPaymentMethods.as_view(), name='payment_methods')
]
