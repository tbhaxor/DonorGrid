from django.http import JsonResponse
from .models import PaymentMethod, CustomField


# Create your views here.
def get_active_payment_methods(request):
    payment_methods = PaymentMethod.objects.filter(is_active=True).values('id', 'provider', 'client_key', 'environment')
    return JsonResponse(data=list(payment_methods), safe=False)


def get_custom_fields(request):
    fields = CustomField.objects.values()
    return JsonResponse(data=list(fields), safe=False)
