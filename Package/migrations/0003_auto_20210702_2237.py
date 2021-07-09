# Generated by Django 3.2.5 on 2021-07-02 22:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Package', '0002_auto_20210702_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='description',
            field=models.TextField(blank=True, default='', max_length=256),
        ),
        migrations.AlterField(
            model_name='package',
            name='recurring_interval',
            field=models.CharField(blank=True, choices=[('month', 'Monthly'), ('year', 'Yearly')], default='month', help_text='Set this if you want to make this package recurring', max_length=10),
        ),
        migrations.AlterField(
            model_name='package',
            name='recurring_unit',
            field=models.IntegerField(blank=True, help_text='Set this if you want to make this package recurring', null=True, validators=[django.core.validators.MinValueValidator(1, message='Recurring unit must be greater than 0')]),
        ),
    ]