from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Donor
from faker import Faker
from faker.providers import internet, profile, person
from time import time
from random import choice


# Create your tests here.
class DonorModelTest(TestCase):
    def setUp(self) -> None:
        Faker.seed(time())
        self.fake = Faker()
        self.fake.add_provider(internet)
        self.fake.add_provider(profile)
        self.fake.add_provider(person)

        self.data = {
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'email': self.fake.email(),
            'phone_number': self.fake.phone_number(),
            'is_anonymous': choice([True, False])
        }
        pass

    def testCreation(self):
        donor: Donor = Donor.objects.create(**self.data)

        self.assertEqual(donor.first_name, self.data['first_name'], 'First name is incorrect')
        self.assertEqual(donor.last_name, self.data['last_name'], 'Last name is incorrect')
        self.assertEqual(donor.email, self.data['email'], 'Email is incorrect')
        self.assertEqual(donor.phone_number, self.data['phone_number'], 'Phone number is incorrect')
        self.assertEqual(donor.is_anonymous, self.data['is_anonymous'], 'Anonymous flag is incorrect')
        return donor

    def testUpdate(self):
        donor = self.testCreation()
        old_name = donor.first_name
        self.data['first_name'] = self.fake.first_name()

        donor.first_name = self.data['first_name']
        donor.save()

        self.assertNotEqual(old_name, donor.first_name)
        self.assertEqual(donor.first_name, self.data['first_name'])
        pass

    def testDelete(self):
        donor = self.testCreation()
        n_old = Donor.objects.count()

        donor.delete()

        n_new = Donor.objects.count()

        self.assertEqual(n_old, 1, 'Incorrect count of donors')
        self.assertEqual(n_new, 0, 'Incorrect count of donors')
        pass

    def testEmailRequiredValidation(self):
        with self.assertRaises(IntegrityError):
            Donor.objects.create(**{**self.data, 'email': None})
            pass
        pass

    def testFirstNameRequiredValidation(self):
        with self.assertRaises(IntegrityError):
            Donor.objects.create(**{**self.data, 'first_name': None})
            pass
        pass

    def testLastNameRequiredValidation(self):
        with self.assertRaises(IntegrityError):
            Donor.objects.create(**{**self.data, 'last_name': None})
            pass
        pass

    pass
