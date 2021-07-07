from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentMethod(models.Model):
	class PaymentProvider(models.TextChoices):
		STRIPE = 'stripe', _('Stripe')
		PAYPAL = 'paypal', _('PayPal')
		RAZORPAY = 'razorpay', _('RazorPay')

	class PaymentEnvironment(models.TextChoices):
		DEVELOPMENT = 'dev', _('Development'),
		PRODUCTION = 'prod', _('Production')

	provider = models.CharField(max_length=15, choices=PaymentProvider.choices, default=PaymentProvider.STRIPE)
	secret_key = models.CharField(max_length=150, null=False, default=None)
	client_key = models.CharField(max_length=150, null=False, default=None)
	pass
