from django.http import JsonResponse, HttpRequest, HttpResponseNotFound, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import Donor, Donation, Package


@csrf_exempt
def create_donation(request: HttpRequest):
    if request.POST.get('package', None) is None and float(request.POST.get('amount', 0)) <= 0:
        return HttpResponseForbidden('amount or package id is required')
    package = Package.objects.filter(id=request.POST.get('package', -1)).first()

    if package is None and float(request.POST.get('amount', 0)) <= 0:
        return HttpResponseNotFound('package %s not found' % request.POST['package'])

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
    return JsonResponse(data={'success': True, 'message': 'Donation has been made'})

