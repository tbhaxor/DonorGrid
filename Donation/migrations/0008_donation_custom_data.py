# Generated by Django 3.2.5 on 2021-08-12 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Donation', '0007_auto_20210717_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='custom_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
