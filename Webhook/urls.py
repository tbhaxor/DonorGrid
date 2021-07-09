from django.urls import path
from .views import stripe, razorpay, paypal

app_name = "webhook"
urlpatterns = [
    path('paypal', paypal),
    path('stripe', stripe),
    path('razorpay', razorpay),
]
