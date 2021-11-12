import json
from django.http import JsonResponse, HttpRequest, HttpResponseForbidden, HttpResponsePermanentRedirect, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from .models import Donor, Donation, Package
from Configuration.models import PaymentMethod, CustomField, SMTPServer, Automation
from Configuration.utils import send_email, send_webhook_event
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
from base64 import b64decode


@csrf_exempt
def create_donation(request: HttpRequest):
    if request.method == 'GET':
        return HttpResponseNotAllowed(permitted_methods=['POST'])

    if request.POST.get('package', None) is None and float(request.POST.get('amount', 0)) <= 0:
        return JsonResponse({'success': False, 'message': 'Amount or package id is required'}, status=400)
    package: Package = Package.objects.filter(id=request.POST.get('package', -1)).first()

    payment_method: PaymentMethod = PaymentMethod.objects.filter(is_active=True, provider=request.POST.get('gateway', None)).first()
    if payment_method is None:
        return JsonResponse({'success': False, 'message': 'Gateway not found'}, status=400)

    if package is None and float(request.POST.get('amount', 0)) <= 0:
        return JsonResponse({'success': False, 'message': 'Package %s not found' % request.POST['package']}, status=400)

    donor, is_created = Donor.objects.get_or_create(email=request.POST.get('email', None), defaults={
        'first_name': request.POST.get('first_name', None),
        'last_name': request.POST.get('last_name', None),
        'email': request.POST.get('email', None),
        'is_anonymous': request.POST.get('is_anonymous', 'no') == 'yes',
        'phone_number': request.POST.get('phone_number', None)
    })

    custom_fields = {}
    raw_fields: dict = json.loads(b64decode(request.POST.get('custom_data', 'e30=')).decode())
    for k, v in raw_fields.items():
        if CustomField.objects.filter(name=k).count():
            custom_fields[k] = v
        pass
    custom_fields = custom_fields if custom_fields.keys() else None

    donation = Donation(donor=donor, package=package, on_behalf_of=request.POST.get('on_behalf_of', ''), note=request.POST.get('note', ''),
                        custom_data=custom_fields)
    if is_created:
        send_webhook_event(Automation.EventChoice.ON_DONOR_CREATE, donation=donation)

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
            send_webhook_event(Automation.EventChoice.ON_PAYMENT_FAIL, donation=donation, fail_reason=message)
            return JsonResponse({'success': False, 'message': message})
        donation.txn_id = paypal_payment.id
        donation.save()
        redirect_url = [*filter(lambda x: x['rel'] == 'approval_url', paypal_payment.links)][0]['href']
        return HttpResponsePermanentRedirect(redirect_to=redirect_url)
    elif payment_method.provider == PaymentMethod.PaymentProvider.STRIPE:
        try:
            token = request.POST.get('token', None)
            if token is None:
                donation.delete()
                return JsonResponse({'success': False, 'message': 'Payment method token required'})

            stripe_payment = PaymentIntent.create(api_key=payment_method.secret_key,
                                                  amount=int(donation.amount * 100),
                                                  currency=donation.currency.lower(),
                                                  confirm=True,
                                                  receipt_email=donor.email,
                                                  payment_method=token,
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
                send_email(donation.donor.email,
                           SMTPServer.EventChoices.ON_PAYMENT_FAIL if not donation.is_completed else SMTPServer.EventChoices.ON_PAYMENT_SUCCESS)

                if not donation.is_completed:
                    last_error = stripe_payment.get('last_payment_error', {})
                    message = last_error.get('message', 'Something went wrong. Stripe payment set to %s' % stripe_payment['status'])
                    send_webhook_event(Automation.EventChoice.ON_PAYMENT_FAIL, donation=donation, fail_reason=message)
                    return JsonResponse({'success': False, 'message': message})
        except (StripeError, CardError, InvalidRequestError) as e:
            donation.delete()
            send_email(donation.donor.email, SMTPServer.EventChoices.ON_PAYMENT_FAIL)
            send_webhook_event(Automation.EventChoice.ON_PAYMENT_FAIL, donation=donation, fail_reason=e)
            return JsonResponse(data={'success': False, 'message': e.user_message})
        pass
    else:
        try:
            token = request.POST.get('token', None)
            if token is None:
                donation.delete()
                return JsonResponse(data={'success': False, 'message': 'Payment method token required'})
            client: RZPayment = Client(auth=(payment_method.client_key, payment_method.secret_key)).payment
            rz_payment: dict = client.fetch(token)
            if rz_payment.get('status') != 'authorized':
                donation.delete()
                send_email(donation.donor.email, SMTPServer.EventChoices.ON_PAYMENT_FAIL)
                send_webhook_event(Automation.EventChoice.ON_PAYMENT_FAIL, donation=donation, fail_reason='Unprocessable payment token passed')
                return JsonResponse(data={'success': False, 'message': 'Unprocessable payment token passed'})

            client.capture(token, rz_payment.get('amount'), {'currency': rz_payment.get('currency')})
            donation.txn_id = token
            donation.is_completed = True
            donation.save()
            send_email(donation.donor.email, SMTPServer.EventChoices.ON_PAYMENT_SUCCESS)
        except BadRequestError as e:
            donation.delete()
            send_email(donation.donor.email, SMTPServer.EventChoices.ON_PAYMENT_FAIL)
            send_webhook_event(SMTPServer.EventChoices.ON_PAYMENT_FAIL, donation=donation, fail_reason=e)
            return JsonResponse(data={'success': False, 'message': e.args[0]})

    send_email(donation.donor.email, SMTPServer.EventChoices.ON_PAYMENT_SUCCESS)
    send_webhook_event(Automation.EventChoice.ON_PAYMENT_SUCCESS, donation=donation)
    return JsonResponse(data={'success': True, 'message': 'Donation has been made'})
