from django.urls import path
from .views import paypal_execute, paypal_cancel, stripe_confirm

app_name = "callback"
urlpatterns = [
    path('paypal/execute', paypal_execute, name='paypal_execute'),
    path('paypal/cancel', paypal_cancel, name='paypal_cancel'),
    path('stripe/confirm', stripe_confirm, name='stripe_confirm')
]
