from django.test import TestCase, Client
from django.template import Context
from django.contrib.messages.storage.base import Message
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.conf import settings
from faker import Faker
from faker.providers import internet, profile, python
from time import time
from .models import PaymentMethod
from typing import List
import os
import functools
import operator


# Create your tests here.
class PaymentMethodTesting(TestCase):
    def setUp(self) -> None:
        os.environ['CI'] = 'True'
        Faker.seed(time())
        self.fake = Faker()
        self.fake.add_provider(internet)
        self.fake.add_provider(profile)
        self.fake.add_provider(python)

        credentials = {
            'username': self.fake.profile()['username'],
            'password': self.fake.mac_address()
        }
        user = User.objects.create_superuser(**credentials)
        user.set_password(credentials['password'])

        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(**credentials), 'Login failed')
        pass

    def testCreatePaymentMethod(self):
        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        r = self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'stripe',
            'client_key': client_key,
            'secret_key': secret_key,
            '_save': 'Save'}, follow=True)
        ctx: Context = r.context

        messages: List[Message] = list(ctx.get('messages'))
        self.assertIsNone(ctx.get('errors'), 'Request failed with errors')
        self.assertEqual(len(messages), 2, 'CI tests tampered')
        self.assertEqual(messages[0].message, 'CI Test Run', 'CI environment not set')
        self.assertRegex(messages[1].message, r"^The payment method.+was added successfully.$", 'Payment method add message is incorrect')

        payment_method = PaymentMethod.objects.first()
        self.assertIsNotNone(payment_method, 'Payment method is not stored in DB')
        self.assertEqual(client_key, payment_method.client_key, 'Client key saved in DB is incorrect')
        self.assertEqual(secret_key, payment_method.secret_key, 'Secret key saved in DB is incorrect')
        pass

    def testSamePaymentMethodProviderTwice(self):
        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        r = self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'stripe',
            'client_key': client_key,
            'secret_key': secret_key,
            'is_active': 'on',
            '_save': 'Save'}, follow=True)
        self.assertIsNone(r.context.get('errors'), 'Request failed with errors')

        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        r = self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'stripe',
            'client_key': client_key,
            'secret_key': secret_key,
            'is_active': 'on',
            '_save': 'Save'}, follow=True)
        self.assertIsNone(r.context.get('errors'), 'Request failed with errors')

        first_payment_method = PaymentMethod.objects.first()
        second_payment_method = PaymentMethod.objects.last()
        self.assertIsNotNone(first_payment_method, 'First payment method not exists')
        self.assertIsNotNone(second_payment_method, 'Second payment method not exists')

        self.assertFalse(first_payment_method.is_active, 'Old payment method is not deactivated')
        self.assertTrue(second_payment_method.is_active, 'New payment method is inactive')
        pass

    def testRequireEnvironmentInPaypal(self):
        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        r = self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'paypal',
            'client_key': client_key,
            'secret_key': secret_key,
            'is_active': 'on',
            '_save': 'Save'}, follow=True)
        ctx: Context = r.context

        errors = ctx.get('errors').data
        errors = functools.reduce(operator.iconcat, errors, [])
        self.assertEqual(len(errors), 1, 'Not failing when environment is not passed')
        self.assertIn('PayPal needs environment details to setup', errors, 'PayPal specific error not found')

        r = self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'paypal',
            'client_key': client_key,
            'secret_key': secret_key,
            'is_active': 'on',
            'environment': 'dev',
            '_save': 'Save'}, follow=True)
        ctx: Context = r.context
        self.assertIsNone(ctx.get('errors'), 'Paypal payment method is failing for valid environment')
        pass

    def testFailOverForDifferentProvider(self):
        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        provider = self.fake.pystr()
        r = self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': provider,
            'client_key': client_key,
            'secret_key': secret_key,
            'is_active': 'on',
            '_save': 'Save'}, follow=True)
        ctx: Context = r.context
        errors = functools.reduce(operator.iconcat, ctx.get('errors'), [])

        self.assertIsNotNone(ctx.get('errors'), 'Error should be thrown')
        self.assertEqual(len(errors), 1, 'Exactly one error required')
        self.assertEqual('Select a valid choice. %s is not one of the available choices.' % provider, errors[0])
        pass

    def testFailOverForDifferentEnv(self):
        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        environment = self.fake.pystr()
        r = self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'stripe',
            'client_key': client_key,
            'secret_key': secret_key,
            'is_active': 'on',
            'environment': environment,
            '_save': 'Save'}, follow=True)
        ctx: Context = r.context
        errors = functools.reduce(operator.iconcat, ctx.get('errors'), [])

        self.assertIsNotNone(ctx.get('errors'), 'Error should be thrown')
        self.assertEqual(len(errors), 1, 'Exactly one error required')
        self.assertEqual('Select a valid choice. %s is not one of the available choices.' % environment, errors[0])
        pass

    def testShowWebhookMessageForRazorPay(self):
        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()

        r = self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'razorpay',
            'client_key': client_key,
            'secret_key': secret_key,
            'is_active': 'on',
            'environment': 'dev',
            '_save': 'Save'}, follow=True)
        ctx: Context = r.context
        self.assertIsNone(ctx.get('errors'), 'Error should not be thrown')

        messages: List[Message] = list(ctx.get('messages'))
        self.assertEqual(len(messages), 2, 'Exactly two messages are required')
        self.assertEqual(messages[0].message, 'Add a webhook URL with endpoint "<strong>%s/webhooks/razorpay</strong>" in your razorpay dashboard' % settings.BASE_URL,
                         'Webhook message in razorpay is not expected')
        self.assertRegex(messages[1].message, r"^The payment method.+was added successfully.$", 'Payment method add message is incorrect')
        pass

    def testPaymentUpdate(self):
        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'stripe',
            'client_key': client_key,
            'secret_key': secret_key,
            '_save': 'Save'}, follow=True)
        old_payment: PaymentMethod = PaymentMethod.objects.first()
        self.assertIsNotNone(old_payment, 'Initial payment method did not exist')

        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        self.client.post(reverse('admin:Configuration_paymentmethod_change', kwargs={'object_id': old_payment.id}), data={
            'provider': 'stripe',
            'client_key': client_key,
            'secret_key': secret_key,
            '_save': 'Save'}, follow=True)
        new_payment: PaymentMethod = PaymentMethod.objects.first()

        self.assertNotEqual(old_payment.client_key, new_payment.client_key, 'Update payment method operation did not work')
        pass

    def testPaymentMethodDelete(self):
        client_key = self.fake.pystr()
        secret_key = self.fake.pystr()
        self.client.post(reverse('admin:Configuration_paymentmethod_add'), data={
            'provider': 'stripe',
            'client_key': client_key,
            'secret_key': secret_key,
            '_save': 'Save'}, follow=True)
        n = PaymentMethod.objects.count()
        self.assertEqual(n, 1, 'Initial payment method did not exist')

        self.client.post(reverse('admin:Configuration_paymentmethod_delete', kwargs={'object_id': 1}), data={'post': 'yes'}, follow=True)

        n = PaymentMethod.objects.count()
        self.assertEqual(n, 0, 'Payment method did not delete')
        pass

    def tearDown(self) -> None:
        self.client.logout()
        pass
    pass
