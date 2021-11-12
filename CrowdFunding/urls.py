from django.urls.conf import path
from .views import get_all_funding, get_one_funding

app_name = 'crowd-funding'

urlpatterns = [
    path('', get_all_funding),
    path('<int:pk>/', get_one_funding)
]
