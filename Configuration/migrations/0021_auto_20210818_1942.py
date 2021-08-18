# Generated by Django 3.2.5 on 2021-08-18 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Configuration', '0020_auto_20210818_1926'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customfield',
            options={'verbose_name': 'Custom Field', 'verbose_name_plural': 'Custom Fields'},
        ),
        migrations.AlterModelOptions(
            name='paymentmethod',
            options={'verbose_name': 'Payment Method Configuration', 'verbose_name_plural': 'Payment Method Configurations'},
        ),
        migrations.AlterModelOptions(
            name='smtpsever',
            options={'verbose_name': 'SMTP Server Config', 'verbose_name_plural': 'SMTP Server Configs'},
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='client_key',
            field=models.CharField(default=None, help_text='Client / Publishable API key of the your payment gateway', max_length=150, unique=True, verbose_name='Client API Key'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='is_active',
            field=models.BooleanField(blank=True, default=False, help_text='Whether to use this payment provider configuration or not. You can have only one type of provider active at a time.', verbose_name='Mark as Active'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='provider',
            field=models.CharField(choices=[('stripe', 'Stripe'), ('paypal', 'PayPal'), ('razorpay', 'RazorPay')], default='stripe', help_text='Select the payment provider of your choice', max_length=15, verbose_name='Payment Provider'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='secret_key',
            field=models.CharField(default=None, help_text='Secret API key of the your payment gateway', max_length=150, unique=True, verbose_name='Secret API Key'),
        ),
    ]