# Generated by Django 3.2.5 on 2021-07-09 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Configuration', '0010_auto_20210709_0651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='wh_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Webhook ID'),
        ),
    ]
