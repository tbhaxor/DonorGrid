# Generated by Django 3.2.5 on 2021-07-23 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Package', '0010_package_is_hidden'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='recurring_interval',
            field=models.CharField(blank=True, choices=[('month', 'Monthly'), ('year', 'Yearly')], help_text='Set this if you want to make this package recurring', max_length=10, null=True),
        ),
    ]
