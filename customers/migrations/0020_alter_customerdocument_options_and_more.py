# Generated by Django 5.1.3 on 2025-01-26 01:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0019_remove_customer_notes_customernote_customer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customerdocument',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='customernote',
            options={'ordering': ['-created_at']},
        ),
    ]
