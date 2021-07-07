from django.urls import path
from .views import AllView, SingleView

app_name = 'package'

urlpatterns = [
    path('', AllView.as_view(), name='all'),
    path('<int:pk>', SingleView.as_view(), name='single'),
]
