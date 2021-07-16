from django.urls import path
from .views import get_all

app_name = 'package'

urlpatterns = [
    path('', get_all, name='all'),
]
