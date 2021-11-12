from django.test import TestCase, Client
from django.test.utils import ContextList
from django.contrib.auth.models import User
from django.contrib.admin.helpers import AdminErrorList
from django.shortcuts import reverse
from .models import Funding
from faker import Faker
from faker.providers import internet, profile, python, currency, lorem
from time import time


# Create your tests here.
class CrowdFundingTest(TestCase):
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
        self.target = self.fake.pyfloat(positive=True, left_digits=3, right_digits=2)
        self.status = self.fake.random.choice([*map(lambda x: x[0], Funding.Status.choices)])
        pass

    def testCreation(self):
        r = self.client.post(reverse('admin:CrowdFunding_funding_add'), data={
            'name': self.name,
            'description': self.description,
            'target': self.target,
            'status': self.status
        }, follow=False)

        errors: AdminErrorList = r.context and r.context[0].get('errors')
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers.get('location'), reverse('admin:CrowdFunding_funding_changelist'))
        self.assertIsNone(errors)
        pass

    def testCreationWithoutName(self):
        r = self.client.post(reverse('admin:CrowdFunding_funding_add'), data={
            'description': self.description,
            'target': self.target,
            'status': self.status
        }, follow=False)

        errors: AdminErrorList = r.context and r.context[0].get('errors')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 1)
        pass

    def testCreationWithoutDescription(self):
        r = self.client.post(reverse('admin:CrowdFunding_funding_add'), data={
            'name': self.name,
            'target': self.target,
            'status': self.status
        }, follow=False)

        errors: AdminErrorList = r.context and r.context[0].get('errors')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 1)
        pass

    def testCreationWithoutTarget(self):
        r = self.client.post(reverse('admin:CrowdFunding_funding_add'), data={
            'name': self.name,
            'description': self.description,
            'status': self.status
        }, follow=False)

        errors: AdminErrorList = r.context and r.context[0].get('errors')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 1)
        pass

    def testCreationWithouStatus(self):
        r = self.client.post(reverse('admin:CrowdFunding_funding_add'), data={
            'name': self.name,
            'description': self.description,
            'target': self.target,
        }, follow=False)

        errors: AdminErrorList = r.context and r.context[0].get('errors')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 1)
        pass

    def testTargetValidator(self):
        r = self.client.post(reverse('admin:CrowdFunding_funding_add'), data={
            'name': self.name,
            'description': self.description,
            'target': 0.0,
            'status': self.status
        }, follow=False)

        errors: AdminErrorList = r.context and r.context[0].get('errors')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 1)
        pass

    def testDeletion(self):
        self.testCreation()

        obj = Funding.objects.first()
        if obj is None:
            self.testCreation()
            obj = Funding.objects.first()

        self.client.post(reverse('admin:CrowdFunding_funding_delete', kwargs={'object_id': obj.id}), data={'post': 'yes'})

        self.assertEqual(Funding.objects.count(), 0)
        pass

    def testUpdate(self):
        self.testCreation()

        obj = Funding.objects.first()
        if obj is None:
            self.testCreation()
            obj = Funding.objects.first()

        name = self.fake.name()
        description = self.fake.paragraph()
        target = self.fake.pyfloat(positive=True, left_digits=3, right_digits=2)
        if obj.status == Funding.Status.ACTIVE:
            obj.status = Funding.Status.INACTIVE
        else:
            obj.status = Funding.Status.ACTIVE
        status = self.fake.random.choice([*map(lambda x: x[0], Funding.Status.choices)])

        self.client.post(reverse('admin:CrowdFunding_funding_change', kwargs={'object_id': obj.id}),
                         data={'name': name,
                               'description': description,
                               'target': target,
                               'status': status},
                         follow=True)
        self.assertNotEqual(name, obj.name)
        self.assertNotEqual(description, obj.description)
        self.assertNotEqual(status, obj.status)
        self.assertNotEqual(target, obj.target)
        pass

    def tearDown(self) -> None:
        self.client.logout()

    pass
