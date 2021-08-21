from django.test import TestCase, Client
from django.template import Context
from django.contrib.messages.storage.base import Message
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.conf import settings
from django.db.utils import IntegrityError
from django.db import transaction
from faker import Faker
from faker.providers import internet, profile, python, lorem, misc
from time import time
from .models import PaymentMethod, CustomField, SMTPServer, Automation
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
        self.assertRegex(messages[1].message, r"^The Payment Method.+was added successfully.$", 'Payment method add message is incorrect')

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
        self.assertRegex(messages[1].message, r"^The Payment Method.+was added successfully.$", 'Payment method add message is incorrect')
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


class CustomFieldTesting(TestCase):
    """
    Since there is no custom form, so here testing should be done directly on the model
    """
    def setUp(self) -> None:
        os.environ['CI'] = 'True'
        Faker.seed(time())
        self.fake = Faker()
        self.fake.add_provider(profile)
        self.fake.add_provider(lorem)

        simple_profile = self.fake.simple_profile()
        paragraph = self.fake.paragraph()

        self.properties = {
            'name': simple_profile['name'],
            'placeholder': 'Enter the value of %s' % simple_profile['username'],
            'attributes': {'id': simple_profile['username']},
            'type': 'text',
            'help_text': paragraph
        }
        pass

    def testCreateField(self):
        field = CustomField.objects.create(**self.properties)

        self.assertEqual(field.__str__(), 'Custom Field %s of type %s' % (field.name, field.type), '__str__() value is wrong')
        self.assertEqual(field.name, self.properties['name'], 'name field value differs')
        self.assertEqual(field.placeholder, self.properties['placeholder'], 'placeholder field value differs')
        self.assertEqual(field.attributes['id'], self.properties['attributes']['id'], 'attribute.id field value differs')
        self.assertEqual(field.type, self.properties['type'], 'type field value differs')
        self.assertEqual(field.help_text, self.properties['help_text'], 'help_text field value differs')

        return field

    def testCustomFieldUpdate(self):
        field = self.testCreateField()

        self.properties['name'] = self.fake.simple_profile()['name']
        CustomField.objects.filter(id=field.id).update(**self.properties)

        field: CustomField = CustomField.objects.filter(id=field.id).first()

        self.assertIsNotNone(field, 'Custom field not exists in db')
        self.assertEqual(field.__str__(), 'Custom Field %s of type %s' % (field.name, field.type), '__str__() value is wrong')
        self.assertEqual(field.name, self.properties['name'], 'name field value differs')
        pass

    def testNameNotNullValidation(self):
        with self.assertRaisesMessage(IntegrityError, 'NOT NULL constraint failed: Configuration_customfield.name'):
            CustomField.objects.create(**{**self.properties, 'name': None})
        pass

    def testTypeNotNullValidation(self):
        with self.assertRaisesMessage(IntegrityError, 'NOT NULL constraint failed: Configuration_customfield.type'):
            CustomField.objects.create(**{**self.properties, 'type': None})
        pass
    pass


class SMTPServerTesting(TestCase):
    def setUp(self) -> None:
        os.environ['CI'] = 'True'
        Faker.seed(time())
        self.fake = Faker()
        self.fake.add_provider(profile)
        self.fake.add_provider(lorem)
        self.fake.add_provider(internet)
        self.fake.add_provider(misc)

        simple_profile = self.fake.simple_profile()

        self.payload = {
            'host': self.fake.hostname(),
            'username': simple_profile['username'],
            'password': self.fake.password(),
            'subject': self.fake.paragraph(),
            'template': self.fake.paragraph(),
            'from_email': simple_profile['mail'],
            'from_name': simple_profile['name']
        }
        pass

    def testCreate(self):
        SMTPServer.objects.create(**self.payload)

        server: SMTPServer = SMTPServer.objects.first()

        self.assertIsNotNone(server, 'Model is not saved')
        self.assertEqual(server.host, self.payload['host'])
        self.assertEqual(server.username, self.payload['username'])
        self.assertEqual(server.password, self.payload['password'])
        self.assertEqual(server.subject, self.payload['subject'])
        self.assertEqual(server.template, self.payload['template'])
        self.assertEqual(server.from_name, self.payload['from_name'])
        self.assertEqual(server.from_email, self.payload['from_email'])

        return server

    def fieldNullCheck(self, field):
        try:
            del self.payload[field]
        except KeyError:
            self.payload[field] = None

        with transaction.atomic():
            with self.assertRaisesMessage(IntegrityError, 'NOT NULL constraint failed: Configuration_smtpserver.%s' % field):
                SMTPServer.objects.create(**self.payload)
        pass

    def testHostNameNullValidator(self):
        self.fieldNullCheck('host')
        pass

    def testUsernameNullValidator(self):
        self.fieldNullCheck('username')
        pass

    def testPasswordNullValidation(self):
        self.fieldNullCheck('password')
        pass

    def testPortNullValidation(self):
        self.fieldNullCheck('port')
        pass

    def testSubjectNullValidation(self):
        self.fieldNullCheck('subject')
        pass

    def testTemplateNullValidation(self):
        self.fieldNullCheck('template')
        pass

    def testEventNullValidation(self):
        self.fieldNullCheck('event')
        pass

    def testUpdate(self):
        old_smtp: SMTPServer = self.testCreate()

        self.payload['host'] = self.fake.hostname()
        SMTPServer.objects.filter(id=old_smtp.id).update(host=self.payload['host'])

        new_smtp: SMTPServer = SMTPServer.objects.first()
        self.assertIsNotNone(new_smtp, 'Object got deleted')

        self.assertNotEqual(new_smtp.host, old_smtp.host, 'Host data not changed')
        pass

    def testDelete(self):
        smtp = self.testCreate()
        smtp.delete()

        count = SMTPServer.objects.count()
        self.assertEqual(count, 0, 'Unable to delete object from db')
        pass
    pass


class AutomationTesting(TestCase):
    def setUp(self) -> None:
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

        self.payload = {
            'name': self.fake.simple_profile()['name'],
            'webhook_url': 'https://hooks.zapier.com/hooks/',
        }
        pass

    def testCreation(self):
        automation = Automation.objects.create(**self.payload)

        self.assertIsNotNone(automation, 'Unable to store the object in db')
        self.assertEqual(automation.name, self.payload['name'], 'Name does not match')
        self.assertEqual(automation.webhook_url, self.payload['webhook_url'], 'Webhook URL does not match')
        self.assertEqual(automation.event, Automation.EventChoice.ON_DONOR_CREATE, 'Default event type %s not set' % Automation.EventChoice.ON_DONOR_CREATE)
        self.assertEqual(automation.service, Automation.ServiceChoice.ZAPIER, 'Default automation service %s not set' % Automation.ServiceChoice.ZAPIER)

        return automation

    def fieldNullCheck(self, field):
        try:
            del self.payload[field]
        except KeyError:
            self.payload[field] = None

        with transaction.atomic():
            with self.assertRaisesMessage(IntegrityError, 'NOT NULL constraint failed: Configuration_automation.%s' % field):
                Automation.objects.create(**self.payload)
        pass

    def testNameFieldNullValidation(self):
        self.fieldNullCheck('name')
        pass

    def testWebhookUrlFieldNullValidation(self):
        self.fieldNullCheck('webhook_url')
        pass

    def testEventFieldNullValidation(self):
        self.fieldNullCheck('event')
        pass

    def testServiceFieldNullValidation(self):
        self.fieldNullCheck('service')
        pass

    def testWrongEventTypeValidation(self):
        self.payload['event'] = Automation.ServiceChoice.ZAPIER
        r = self.client.post(reverse('admin:Configuration_automation_add'), data=self.payload, follow=False)
        ctx: Context = r.context

        self.assertIsNotNone(ctx, 'Response context is none')
        self.assertIsNotNone(ctx.get('errors'), 'Response does not contain error in wrong payload')
        errors = ctx.get('errors').data
        errors = functools.reduce(operator.iconcat, errors, [])

        self.assertGreaterEqual(len(errors), 1, 'No error found in the list')
        self.assertIn('Select a valid choice. zapier is not one of the available choices.', errors, 'Choice validation error not found')
        pass

    def testWrongServiceTypeValidation(self):
        self.payload['service'] = Automation.EventChoice.ON_DONOR_CREATE
        r = self.client.post(reverse('admin:Configuration_automation_add'), data=self.payload, follow=False)
        ctx: Context = r.context

        self.assertIsNotNone(ctx, 'Response context is none')
        self.assertIsNotNone(ctx.get('errors'), 'Response does not contain error in wrong payload')
        errors = ctx.get('errors').data
        errors = functools.reduce(operator.iconcat, errors, [])

        self.assertGreaterEqual(len(errors), 1, 'No error found in the list')
        self.assertIn('Select a valid choice. on_donor_create is not one of the available choices.', errors, 'Choice validation error not found')
        pass

    def testWrongServiceWebhookUrlValidation(self):
        self.payload['webhook_url'] = 'https://gibberish.com'
        self.payload['service'] = Automation.ServiceChoice.ZAPIER
        r = self.client.post(reverse('admin:Configuration_automation_add'), data=self.payload, follow=False)
        ctx: Context = r.context

        self.assertIsNotNone(ctx, 'Response context is none')
        self.assertIsNotNone(ctx.get('errors'), 'Response does not contain error in wrong payload')

        errors = ctx.get('errors').data
        errors = functools.reduce(operator.iconcat, errors, [])

        self.assertGreaterEqual(len(errors), 1, 'No error found in the list')
        self.assertIn('Invalid url hostname', errors, 'Choice validation error not found')
        pass

    def testWebhookUrlFieldType(self):
        self.payload['webhook_url'] = 'gibberish'
        r = self.client.post(reverse('admin:Configuration_automation_add'), data=self.payload, follow=False)
        ctx: Context = r.context

        self.assertIsNotNone(ctx, 'Response context is none')
        self.assertIsNotNone(ctx.get('errors'), 'Response does not contain error in wrong payload')

        errors = ctx.get('errors').data
        errors = functools.reduce(operator.iconcat, errors, [])

        self.assertGreaterEqual(len(errors), 1, 'No error found in the list')
        self.assertIn('Enter a valid URL.', errors, 'URL validation failed')
        pass

    def testUpdate(self):
        old_automation = self.testCreation()

        self.payload['name'] = self.fake.simple_profile()['name']
        Automation.objects.filter(id=old_automation.id).update(**self.payload)

        new_automation: Automation = Automation.objects.first()
        self.assertIsNotNone(new_automation, 'Object deleted from db after update')
        self.assertNotEqual(old_automation.name, new_automation.name, 'Updated field did not change')
        self.assertEqual(old_automation.webhook_url, new_automation.webhook_url, 'Untouched fields also changed')
        pass

    def testDelete(self):
        automation = self.testCreation()
        automation.delete()

        count = Automation.objects.count()
        self.assertEqual(count, 0, 'Object is not removed from db')
        pass

    def tearDown(self):
        self.client.logout()
    pass
