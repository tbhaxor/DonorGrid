from django.http.request import HttpRequest
from django.http.response import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.db.models.aggregates import Sum
from .models import Funding


@csrf_exempt
def get_funding_response_object(funding: Funding):
    donations = funding.donations.aggregate(Sum('amount'))
    return {
        'id': funding.id,
        'name': funding.name,
        'description': funding.description,
        'target': funding.target,
        'donated_amount': donations['amount__sum'] or 0
    }


@csrf_exempt
def get_all_funding(request: HttpRequest):
    funding_qs = Funding.objects.exclude(status=Funding.Status.INACTIVE)

    fundings = []

    for funding in funding_qs:
        fundings.append(get_funding_response_object(funding))

    return JsonResponse(fundings, safe=False)


@csrf_exempt
def get_one_funding(request: HttpRequest, pk: int):
    print("Hello")
    funding = Funding.objects.filter(id=pk).exclude(status=Funding.Status.INACTIVE).first()
    if funding is None:
        return JsonResponse({
            'success': False,
            'message': f'Funding with ID {pk} not found'
        }, status=404)

    return JsonResponse(get_funding_response_object(funding), safe=True)
