# Generated by Django 3.2.5 on 2021-08-21 02:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Configuration', '0023_rename_smtpsever_smtpserver'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='paymentmethod',
            options={'verbose_name': 'Payment Method', 'verbose_name_plural': 'Payment Methods'},
        ),
        migrations.AlterModelOptions(
            name='smtpserver',
            options={'verbose_name': 'SMTP Server', 'verbose_name_plural': 'SMTP Servers'},
        ),
    ]