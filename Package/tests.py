from django.test import TestCase, Client
from django.template import Context
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Package
from faker import Faker
from faker.providers import internet, profile, python, currency, lorem
from time import time
from decimal import Decimal
import functools
import operator


# Create your tests here.
class PackageCRUD(TestCase):
    def setUp(self) -> None:
        self.client = Client(enforce_csrf_checks=False)
        Faker.seed(time())
        self.fake = Faker()
        self.fake.add_provider(internet)
        self.fake.add_provider(profile)
        self.fake.add_provider(python)
        self.fake.add_provider(currency)
        self.fake.add_provider(lorem)

        credentials = {
            'username': self.fake.profile()['username'],
            'password': self.fake.mac_address()
        }
        user = User.objects.create_superuser(**credentials)
        user.set_password(credentials['password'])

        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(**credentials), 'Login failed')

        self.name = self.fake.name()
        self.description = self.fake.paragraph()
        self.amount = self.fake.pyfloat(positive=True, left_digits=3, right_digits=4)
        self.curr = self.fake.currency_code()
        pass

    def testCreatePackage(self):
        r = self.client.post(reverse('admin:Package_package_add'), data={
            'name': self.name,
            'description': self.description,
            'amount': round(self.amount, 2),
            'currency': self.curr
        }, follow=False)

        self.assertEqual(r.headers.get('Location'), reverse('admin:Package_package_changelist'), 'Location header value is incorrect')
        self.assertIsNone(r.context, 'Request context is not None')

        package: Package = Package.objects.first()
        self.assertIsNotNone(package, 'Package object supposed to be committed in db')
        self.assertEqual(package.name, self.name, 'Incorrect package name')
        self.assertEqual(package.amount, round(Decimal(self.amount), 2), 'Incorrect package amount value')
        self.assertEqual(package.description, self.description, 'Incorrect package description text')
        self.assertEqual(package.currency, self.curr, 'Incorrect package currency')
        self.assertIsNone(package.recurring_unit, 'Recurring unit is not None by default')
        self.assertIsNone(package.recurring_interval, 'Recurring interval is not None by default')
        return package

    def testUpdate(self):
        old_package = self.testCreatePackage()

        self.name = self.fake.name()
        self.curr = self.fake.currency_code()
        self.client.post(reverse('admin:Package_package_change', kwargs={'object_id': old_package.id}), data={
            'name': self.name,
            'description': old_package.description,
            'amount': old_package.amount,
            'currency': self.curr
        })

        new_package: Package = Package.objects.first()
        self.assertEqual(old_package.id, new_package.id, 'Package ID is not same')
        self.assertEqual(self.name, new_package.name, 'Package name differs')
        self.assertNotEqual(old_package.name, new_package.name, 'Package name didnt change')
        self.assertEqual(self.curr, new_package.currency, 'Currency code differs')
        self.assertNotEqual(old_package.currency, new_package.currency, 'Currency code didnt change')
        pass

    def testDeletePackage(self):
        old_package = self.testCreatePackage()

        self.client.post(reverse('admin:Package_package_delete', kwargs={'object_id': old_package.id}), data={'post': 'yes'})

        new_package = Package.objects.first()
        self.assertIsNone(new_package, 'Unable to delete package')
        pass

    def testValidateAmountDecimal(self):
        r = self.client.post(reverse('admin:Package_package_add'), data={
            'name': self.name,
            'description': self.description,
            'amount': self.amount,
            'currency': self.curr
        }, follow=False)

        ctx: Context = r.context
        self.assertIsNone(r.headers.get('Location'), 'Location header is not None on incorrect data')
        self.assertIsNotNone(ctx.get('errors'), 'Errors object is None on incorrect data')

        errors = functools.reduce(operator.iconcat, ctx.get('errors'))
        self.assertIn('Ensure that there are no more than 2 decimal places.', errors, 'Amount decimal validation')

        r = self.client.post(reverse('admin:Package_package_add'), data={
            'name': self.name,
            'description': self.description,
            'amount': round(self.amount, 2),
            'currency': self.curr,
        }, follow=False)

        self.assertIsNotNone(r.headers.get('Location'), 'Location header is None on correct data')
        pass

    def testRequiredName(self):
        r = self.client.post(reverse('admin:Package_package_add'), data={
            'name': '',
            'description': self.description,
            'amount': self.amount,
            'currency': self.curr,
        }, follow=False)

        ctx: Context = r.context

        self.assertIsNone(r.headers.get('Location'), 'Location header is not None on incorrect data')
        self.assertIsNotNone(ctx.get('errors'), 'Errors object is None on incorrect data')

        errors = functools.reduce(operator.iconcat, ctx.get('errors').data)
        self.assertIn('This field is required.', errors)

        r = self.client.post(reverse('admin:Package_package_add'), data={
            'name': self.name,
            'description': self.description,
            'amount': round(self.amount, 2),
            'currency': self.curr,
        }, follow=False)

        self.assertIsNotNone(r.headers.get('Location'), 'Location header is None on correct data')
        pass

    def testRequiredAmount(self):
        r = self.client.post(reverse('admin:Package_package_add'), data={
            'name': self.name,
            'description': self.description,
            'amount': '',
            'currency': self.curr,
        }, follow=False)

        ctx: Context = r.context
        self.assertIsNone(r.headers.get('Location'), 'Location header is not None on incorrect data')
        self.assertIsNotNone(ctx.get('errors'), 'Errors object is None on incorrect data')

        errors = functools.reduce(operator.iconcat, ctx.get('errors').data)
        self.assertIn('This field is required.', errors)

        r = self.client.post(reverse('admin:Package_package_add'), data={
            'name': self.name,
            'description': self.description,
            'amount': round(self.amount, 2),
            'currency': self.curr,
        }, follow=False)

        self.assertIsNotNone(r.headers.get('Location'), 'Location header is None on correct data')
        pass

    def testFailRecurring(self):
        r = self.client.post(reverse('admin:Package_package_add'), data={
            'name': self.name,
            'description': self.description,
            'amount': round(self.amount, 2),
            'currency': self.curr,
            'recurring_interval': 'year'
        }, follow=False)

        ctx: Context = r.context
        self.assertIsNone(r.headers.get('Location'), 'Location header is not None on incorrect data')
        self.assertIsNotNone(ctx.get('errors'), 'Errors object is None on incorrect data')

        errors = functools.reduce(operator.iconcat, ctx.get('errors').data)
        self.assertIn('Recurring packages are not supported yet', errors)
        pass

    def tearDown(self) -> None:
        self.client.logout()
        pass

    pass
