# Generated by Django 3.2.5 on 2021-07-02 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Donor', '0002_alter_donor_first_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donor',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
