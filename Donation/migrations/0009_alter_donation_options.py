# Generated by Django 3.2.5 on 2021-08-18 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Donation', '0008_donation_custom_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donation',
            options={'verbose_name': 'Donation', 'verbose_name_plural': 'Donations'},
        ),
    ]