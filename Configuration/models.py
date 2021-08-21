from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class PaymentMethod(models.Model):
    class PaymentProvider(models.TextChoices):
        STRIPE = 'stripe', _('Stripe')
        PAYPAL = 'paypal', _('PayPal')
        RAZORPAY = 'razorpay', _('RazorPay')

    class PaymentEnvironment(models.TextChoices):
        DEVELOPMENT = 'dev', _('Development')
        PRODUCTION = 'prod', _('Production')

    provider = models.CharField(max_length=15, choices=PaymentProvider.choices, default=PaymentProvider.STRIPE, verbose_name='Payment Provider', help_text='Select the payment provider of your choice')
    secret_key = models.CharField(max_length=150, null=False, default=None, unique=True, verbose_name='Secret API Key', help_text='Secret API key of the your payment gateway')
    client_key = models.CharField(max_length=150, null=False, default=None, unique=True, verbose_name='Client API Key', help_text='Client / Publishable API key of the your payment gateway')
    environment = models.CharField(max_length=4, null=False, blank=True, default=PaymentEnvironment.DEVELOPMENT, choices=PaymentEnvironment.choices, help_text='Required for PayPal')
    is_active = models.BooleanField(default=False, null=False, blank=True, help_text='Whether to use this payment provider configuration or not. You can have only one type of provider active at a '
                                                                                     'time.', verbose_name='Mark as Active')
    wh_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='Webhook ID')

    def __str__(self):
        return 'PaymentMethod %d : %s' % (self.id, self.provider)

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
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
    type = models.CharField(max_length=15, verbose_name='Field Type', help_text='Type of input field to use. Use this as HTML validation', choices=CustomFieldType.choices,
                            default=CustomFieldType.TEXT)
    help_text = models.TextField(max_length=256, verbose_name='Help Text (Optional)', help_text='Enter help description for the field. This should be shown on the checkout page', blank=True,
                                 default='')

    def __str__(self):
        return 'Custom Field %s of type %s' % (self.name, self.type)

    def __repr__(self):
        return self.__str__()
    
    class Meta:
        verbose_name = 'Custom Field'
        verbose_name_plural = 'Custom Fields'
    pass


class SMTPServer(models.Model):
    class SMTPPortChoice(models.IntegerChoices):
        port_25 = 25, _('25 - Insecure')
        port_465 = 465, _('465 - SSL Secure')
        port_587 = 587, _('587 - TLS Secure')
        pass

    class EventChoices(models.TextChoices):
        ON_PAYMENT_SUCCESS = 'success', _('Payment Succeeded')
        ON_PAYMENT_FAIL = 'fail', _('Payment Failed')

    host = models.CharField(max_length=256, help_text='Enter IP/hostname to connect', verbose_name='Hostname', null=False, default=None, blank=False)
    username = models.CharField(max_length=128, help_text='Enter username for authenticating SMTP server', verbose_name='Username', null=False, blank=False, default=None)
    password = models.CharField(max_length=128, help_text='Enter password for authenticating SMTP server', verbose_name='Password', null=False, blank=False, default=None)
    port = models.IntegerField(help_text='Enter port number', verbose_name='Port number', null=False, default=SMTPPortChoice.port_25, choices=SMTPPortChoice.choices, blank=False)
    subject = models.CharField(max_length=128, help_text='Enter email subject', verbose_name='Email Subject', null=False, blank=False, default=None)
    template = RichTextField(verbose_name='Email Body', help_text='Enter email body here', null=False, blank=False, default=None)
    event = models.CharField(max_length=7, verbose_name='Trigger event', help_text='Select when you want to send the email to donors', default=EventChoices.ON_PAYMENT_SUCCESS,
                             choices=EventChoices.choices, null=False, blank=False)
    from_name = models.CharField(max_length=50, verbose_name='From Name', help_text='Enter the name from which you want to send the email', default='DonorGrid', null=False, blank=False)
    from_email = models.CharField(max_length=75, verbose_name='From Email', help_text='Enter the email address from which you want to send the email', default='no_reply@donorgrid.io', null=False,
                                  blank=False)

    def __str__(self):
        return 'SMTP Config - %s' % self.subject

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'SMTP Server'
        verbose_name_plural = 'SMTP Servers'
    pass


class Automation(models.Model):
    class ServiceChoice(models.TextChoices):
        ZAPIER = 'zapier', _('Zapier')
        PABBLY_CONNECT = 'paybbly_connect', _('Pabbly Connect')

    class EventChoice(models.TextChoices):
        ON_PAYMENT_SUCCESS = 'on_payment_success', _('On Payment Success')
        ON_PAYMENT_FAIL = 'on_payment_fail', _('On Payment Fail')
        ON_DONOR_CREATE = 'on_donor_create', _('On Donor Create')

    name = models.CharField(max_length=50, verbose_name='Webhook Entry Name', help_text='Enter a human-friendly webhook name', null=False, blank=False, default=None)
    webhook_url = models.URLField(verbose_name='Webhook URL', null=False, blank=False, default=None)
    event = models.CharField(max_length=20, verbose_name='Trigger Event', choices=EventChoice.choices, default=EventChoice.ON_DONOR_CREATE, null=False, blank=False, help_text='Select when you want '
                                                                                                                                                                               'to trigger this '
                                                                                                                                                                               'webhook')
    service = models.CharField(max_length=20, verbose_name='Automation Service', choices=ServiceChoice.choices, default=ServiceChoice.ZAPIER, null=False, blank=False, help_text='Select the '
                                                                                                                                                                                 'automation service '
                                                                                                                                                                                 'for integration')

    def __str__(self):
        return 'Webhook %s' % self.name

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Automation Service'
        verbose_name_plural = 'Automation Services'
    pass
