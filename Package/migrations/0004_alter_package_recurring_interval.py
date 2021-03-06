# Generated by Django 3.2.5 on 2021-07-02 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Package', '0003_auto_20210702_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='recurring_interval',
            field=models.CharField(blank=True, choices=[('month', 'Monthly'), ('year', 'Yearly')], default=None, help_text='Set this if you want to make this package recurring', max_length=10),
        ),
    ]
