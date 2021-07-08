from django.contrib import admin
from django.forms import ModelForm
from .models import PaymentMethod


class PaymentMethodForm(ModelForm):
    def clean(self):
        if self.cleaned_data.get('provider') == 'paypal' and not self.cleaned_data.get('environment'):
            self.add_error('environment', 'PayPal needs environment details to setup')
            return

        pass

    class Meta:
        model = PaymentMethod
        fields = ['provider', 'secret_key', 'client_key', 'environment', 'is_active']

    pass


@admin.register(PaymentMethod)
class PaymentMethodRegister(admin.ModelAdmin):
    form = PaymentMethodForm
    empty_value_display = 'N/A'
    list_display = ['payment_gateway', 'environment', 'is_active', 'client_key']
    list_display_links = ['payment_gateway']

    fieldsets = (
        (
            'Select Payment Provider', {
                'description':  'Select type of payment provider to configure and environment',
                'fields': ('provider', 'environment')
            }
        ),
        (
            'Configure Keys', {
                'description': 'Goto API dashboard, copy and paste keys here',
                'fields': ('client_key', 'secret_key')
            }
        ),
        (
            'Meta Information', {
                'description': 'Configure payment meta information',
                'fields': ('is_active',)
            }
        )
    )

    def delete_model(self, request, obj: PaymentMethod):
        self.message_user(request, "Please delete the webhook from the dashboard to avoid errors")
        return super(PaymentMethodRegister, self).delete_model(request, obj)

    def save_model(self, request, obj: PaymentMethod, form, change):
        if obj.is_active:
            PaymentMethod.objects.exclude(id=obj.id).filter(provider=obj.provider, is_active=True).update(is_active=False)
            pass

        if obj.provider == 'razorpay':
            self.message_user(request, 'Add a webhook URL in your razorpay dashboard')
        elif obj.provider == 'paypal':
            # TODO: save webhook automatically
            # api = Api({
            #     'mode': 'sandbox' if obj.environment == 'dev' else 'live',
            #     'client_id': obj.client_key,
            #     'client_secret': obj.secret_key
            # })
            pass
        elif obj.provider == 'stripe':
            # TODO: save webhook automatically
            # WebhookEndpoint(api_key=obj.secret_key).create()
            pass
        return super(PaymentMethodRegister, self).save_model(request, obj, form, change)

    def payment_gateway(self, obj: PaymentMethod):
        name = [*filter(lambda x: x[0] == obj.provider, PaymentMethod.PaymentProvider.choices)][0][1]
        return name
    pass
