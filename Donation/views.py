from django.http import JsonResponse, HttpRequest, HttpResponseNotFound, HttpResponseForbidden, HttpResponsePermanentRedirect
from django.views.decorators.csrf import csrf_exempt
from .models import Donor, Donation, Package, PaymentMethod
from django.conf import settings
from django.urls import reverse
from paypalrestsdk.payments import Payment
from paypalrestsdk.api import Api
from stripe.api_resources.payment_intent import PaymentIntent
from stripe.error import InvalidRequestError, CardError, StripeError
from urllib.parse import urlencode
from razorpay.client import Client
from razorpay.resources.payment import Payment as RZPayment
from razorpay.errors import BadRequestError


@csrf_exempt
def create_donation(request: HttpRequest):
    if request.POST.get('package', None) is None and float(request.POST.get('amount', 0)) <= 0:
        return HttpResponseForbidden('Amount or package id is required')
    package: Package = Package.objects.filter(id=request.POST.get('package', -1)).first()

    payment_method: PaymentMethod = PaymentMethod.objects.filter(is_active=True, provider=request.POST.get('gateway', None)).first()
    if payment_method is None:
        return HttpResponseNotFound('Gateway not found')

    if package is None and float(request.POST.get('amount', 0)) <= 0:
        return HttpResponseNotFound('Package %s not found' % request.POST['package'])

    donor = Donor.objects.get_or_create(email=request.POST.get('email', None), defaults={
        'first_name': request.POST.get('first_name', None),
        'last_name': request.POST.get('last_name', None),
        'email': request.POST.get('email', None),
        'is_anonymous': request.POST.get('is_anonymous', 'no') == 'yes',
        'phone_number': request.POST.get('phone_number', None)
    })[0]

    donation = Donation(donor=donor, package=package)
    if package is None:
        donation.currency = request.POST.get('currency', 'USD')
        donation.amount = float(request.POST['amount'])
        pass
    else:
        donation.currency = package.currency
        donation.amount = package.amount
        pass

    donation.save()

    if payment_method.provider == PaymentMethod.PaymentProvider.PAYPAL:
        api = Api({
            'mode': 'sandbox' if payment_method.environment == 'dev' else 'live',
            'client_id': payment_method.client_key,
            'client_secret': payment_method.secret_key
        })

        paypal_payload = {
            'intent': 'sale',
            'payer': {
                'payment_method': 'paypal'
            },
            'redirect_urls': {
                'return_url': settings.BASE_URL + reverse('callback:paypal_execute') + '?' + urlencode({
                    'donation_id': donation.id,
                    'gateway_id': payment_method.id
                }),
                'cancel_url': settings.BASE_URL + reverse('callback:paypal_cancel')
            },
            'transactions': [
                {
                    'item_list': {
                        'items': [
                            {
                                'name': package.name if package else 'Custom Amount',
                                'price': str(donation.amount),
                                'currency': donation.currency,
                                'quantity': 1
                            }
                        ]
                    },
                    'amount': {
                        'total': str(donation.amount),
                        'currency': donation.currency
                    },
                }
            ]
        }

        paypal_payment = Payment(api=api, attributes=paypal_payload)
        if not paypal_payment.create():
            message = paypal_payment.error.get('message', 'Something went wrong')
            if 'details' in paypal_payment.error:
                message = paypal_payment.error['details'][0]['issue']
            donation.delete()
            return JsonResponse(data={'success': False, 'message': message})
        donation.txn_id = paypal_payment.id
        donation.save()
        redirect_url = [*filter(lambda x: x['rel'] == 'approval_url', paypal_payment.links)][0]['href']
        return HttpResponsePermanentRedirect(redirect_to=redirect_url)
    elif payment_method.provider == PaymentMethod.PaymentProvider.STRIPE:
        try:
            rz_token = request.POST.get('token', None)
            if rz_token is None:
                donation.delete()
                return JsonResponse(data={'success': False, 'message': 'Payment method token required'})

            stripe_payment = PaymentIntent.create(api_key=payment_method.secret_key,
                                                  amount=int(donation.amount * 100),
                                                  currency=donation.currency.lower(),
                                                  confirm=True,
                                                  receipt_email=donor.email,
                                                  payment_method=rz_token,
                                                  capture_method='automatic',
                                                  return_url=settings.BASE_URL + reverse('callback:stripe_confirm') + '?' + urlencode({
                                                      'donation_id': donation.id,
                                                      'gateway_id': payment_method.id
                                                  }),
                                                  description='Donation for %s' % settings.BASE_URL
                                                  ).to_dict_recursive()
            donation.txn_id = stripe_payment.get('id')
            donation.save()

            if 'next_action' in stripe_payment and stripe_payment['next_action'] is not None:
                redirect_url = stripe_payment['next_action']['redirect_to_url']['url']
                return HttpResponsePermanentRedirect(redirect_to=redirect_url)
            else:
                donation.is_completed = stripe_payment['status'] == 'succeeded'
                donation.save()
        except (StripeError, CardError, InvalidRequestError) as e:
            donation.delete()
            return JsonResponse(data={'success': False, 'message': e.user_message})
        pass
    else:
        try:
            rz_token = request.POST.get('token', None)
            if rz_token is None:
                donation.delete()
                return JsonResponse(data={'success': False, 'message': 'Payment method token required'})
            client: RZPayment = Client(auth=(payment_method.client_key, payment_method.secret_key)).payment
            rz_payment: dict = client.fetch(rz_token)
            if rz_payment.get('status') != 'authorized':
                donation.delete()
                return JsonResponse(data={'success': False, 'message': 'Unprocessable payment token passed'})

            client.capture(rz_token, rz_payment.get('amount'), {'currency': rz_payment.get('currency')})
            donation.txn_id = rz_token
            donation.is_completed = True
            donation.save()
        except BadRequestError as e:
            donation.delete()
            return JsonResponse(data={'success': False, 'message': e.args[0]})

    return JsonResponse(data={'success': True, 'message': 'Donation has been made'})
