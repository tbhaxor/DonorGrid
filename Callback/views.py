from django.http import HttpRequest, HttpResponseRedirect
from django.conf import settings
from urllib.parse import urlencode
from django.views.decorators.csrf import csrf_exempt
from paypalrestsdk.api import Api
from paypalrestsdk.payments import Payment
from Donation.models import Donation
from Configuration.models import PaymentMethod


# Create your views here.
@csrf_exempt
def paypal_execute(request: HttpRequest):
    print(request.GET)
    donation: Donation = Donation.objects.filter(id=request.GET.get('donation_id', -1)).first()
    payment_method: PaymentMethod = PaymentMethod.objects.filter(id=request.GET.get('gateway_id', -1)).first()
    token = request.GET.get('paymentId', None)
    payer_id = request.GET.get('PayerID', None)

    if donation is None or payment_method is None or token is None or payer_id is None:
        return HttpResponseRedirect(redirect_to=settings.BASE_URL + '?' + urlencode({
            'success': 'false',
            'message': 'Request is not containing processable entities'
        }))

    api = Api({
        'mode': 'sandbox' if payment_method.environment == 'dev' else 'live',
        'client_id': payment_method.client_key,
        'client_secret': payment_method.secret_key
    })

    paypal_payment = Payment.find(resource_id=token, api=api)
    if not paypal_payment.execute({'payer_id': payer_id}):
        message = paypal_payment.error.get('message', 'Something went wrong')
        if 'details' in paypal_payment.error:
            message = paypal_payment.error['details'][0]['issue']
        return HttpResponseRedirect(redirect_to=settings.BASE_URL + '?' + urlencode({
            'success': 'false',
            'message': message
        }))

    donation.is_completed = True
    donation.save()
    return HttpResponseRedirect(redirect_to=settings.BASE_URL + '?' + urlencode({
        'success': 'true',
        'message': 'Donation completed. Thanks for your generosity'
    }))


@csrf_exempt
def paypal_cancel(request: HttpRequest):
    return HttpResponseRedirect(redirect_to=settings.BASE_URL + '?' + urlencode({'success': 'false', 'message': 'Cancelled by the user'}))


@csrf_exempt
def stripe_confirm(request: HttpRequest):
    donation: Donation = Donation.objects.filter(id=request.GET.get('donation_id', -1)).first()

    if donation is None:
        return HttpResponseRedirect(redirect_to=settings.BASE_URL + '?' + urlencode({
            'success': 'false',
            'message': 'Request is not containing processable entities'
        }))

    donation.is_completed = True
    donation.save()
    return HttpResponseRedirect(redirect_to=settings.BASE_URL + '?' + urlencode({
        'success': 'true',
        'message': 'Donation completed. Thanks for your generosity'
    }))

