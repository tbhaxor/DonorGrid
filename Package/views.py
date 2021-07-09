from django.http import HttpRequest, JsonResponse, HttpResponseNotFound
from django.views import View
from .models import Package


# Create your views here.
class AllView(View):

    def get(self, request: HttpRequest):
        packages = Package.objects.exclude(is_hidden=True).values()
        return JsonResponse(data=list(packages), safe=False)
    pass


class SingleView(View):

    def get(self, request: HttpRequest, pk: int):
        try:
            package = Package.objects.values().get(id=pk)
            return JsonResponse(data=dict(package))
        except Package.DoesNotExist:
            return HttpResponseNotFound('Package with id %d not found' % pk)
        pass
    pass
