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
	secret_key = models.CharField(max_length=150, null=False, default=None, unique=True)
	client_key = models.CharField(max_length=150, null=False, default=None, unique=True)
	environment = models.CharField(max_length=4, null=False, blank=True, default=PaymentEnvironment.DEVELOPMENT, choices=PaymentEnvironment.choices, help_text='Required for PayPal')
	# TODO: add intuitive help message
	is_active = models.BooleanField(default=False, null=False, blank=True, help_text='Custom message', verbose_name='Mark as Active')
	wh_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='Webhook ID')

	def __str__(self):
		return 'PaymentMethod %d : %s' % (self.id, self.provider)

	def __repr__(self):
		return self.__str__()
	pass
