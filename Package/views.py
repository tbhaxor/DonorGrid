from django.http import JsonResponse
from .models import Package


# Create your views here.
def get_all(request):
    packages = Package.objects.exclude(is_hidden=True).values('id', 'name', 'description', 'amount', 'currency')
    return JsonResponse(data=list(packages), safe=False)

