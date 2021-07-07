from django.urls import path
from .views import create_donation

app_name = 'donation'

urlpatterns = [
    path('', create_donation, name='create')
]
