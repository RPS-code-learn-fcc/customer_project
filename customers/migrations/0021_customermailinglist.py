# Generated by Django 5.1.3 on 2025-01-29 20:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0020_alter_customerdocument_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerMailingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, validators=[django.core.validators.MinLengthValidator(4), django.core.validators.MaxLengthValidator(50), django.core.validators.RegexValidator(message='Name can only contain letters, spaces, numbers and dashes.', regex='^[a-zA-Z0-9\\s-]+$')])),
                ('addresses', models.ManyToManyField(related_name='mailing_addresses', to='customers.address')),
                ('interests', models.ManyToManyField(related_name='mailing_interests', to='customers.customerinterest')),
            ],
        ),
    ]
