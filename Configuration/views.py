from django.http import HttpRequest, JsonResponse
from django.views import View
from .models import PaymentMethod


# Create your views here.
class AllPaymentMethods(View):
    def get(self, request: HttpRequest):
        payment_methods = PaymentMethod.objects.all().values('id', 'provider', 'client_key', 'environment')
        return JsonResponse(data=list(payment_methods), safe=False)
        pass
    pass
