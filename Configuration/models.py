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


class CustomField(models.Model):
	class CustomFieldType(models.TextChoices):
		URL = 'url', _('URL')
		DATE = 'date', _('Date'),
		DATETIME_LOCAL = 'datetime-local', _('Local DateTime')
		TIME = 'time', _('Time')
		TEL = 'tel', _('Telephone')
		TEXT = 'text', _('Text')
		EMAIL = 'email', _('Email')
		NUMBER = 'number', _('Number')
	
	name = models.CharField(max_length=50, null=False, blank=False, help_text='Unique of the name', verbose_name='Field Name')
	placeholder = models.CharField(max_length=75, null=True, blank=True, help_text='Placeholder text for the input field', verbose_name='Placeholder Text (Optional)')
	attributes = models.JSONField(verbose_name='Attributes (Optional)', blank=True, null=True, help_text='Input tag extra attributes as JSON')
	type = models.CharField(max_length=15, verbose_name='Field Type', help_text='Type of input field to use. Use this as HTML validation', choices=CustomFieldType.choices, default=CustomFieldType.TEXT)
	help_text = models.TextField(max_length=256, verbose_name='Help Text (Optional)', help_text='Enter help description for the field. This should be shown on the checkout page', blank=True, default='')

	def __str__(self):
		return "Custom Field %s of type %s" % (self.name, self.type)

	def __repr__(self):
		return self.__str__()
	pass
