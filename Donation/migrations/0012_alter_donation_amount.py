# Generated by Django 3.2.8 on 2021-11-12 05:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Donation', '0011_alter_donation_funding'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='amount',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
