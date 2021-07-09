from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def paypal(request: HttpRequest):
    print(request.POST)
    print(request.body)
    return HttpResponse("OK")


@csrf_exempt
def stripe(request: HttpRequest):
    return HttpResponse("OK")


@csrf_exempt
def razorpay(request: HttpRequest):
    return HttpResponse("OK")
