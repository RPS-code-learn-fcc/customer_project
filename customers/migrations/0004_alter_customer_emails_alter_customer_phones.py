# Generated by Django 5.1.3 on 2025-01-01 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_customer_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='emails',
            field=models.ManyToManyField(blank=True, related_name='customer_emails', to='customers.email'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phones',
            field=models.ManyToManyField(blank=True, related_name='customer_phones', to='customers.phone'),
        ),
    ]
