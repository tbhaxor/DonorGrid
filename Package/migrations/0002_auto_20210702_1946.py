# Generated by Django 3.2.5 on 2021-07-02 19:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Package', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='recurring_interval',
            field=models.CharField(blank=True, choices=[('month', 'Monthly'), ('year', 'Yearly')], default='month', max_length=10),
        ),
        migrations.AddField(
            model_name='package',
            name='recurring_unit',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1, message='Recurring unit must be greater than 0')]),
        ),
    ]