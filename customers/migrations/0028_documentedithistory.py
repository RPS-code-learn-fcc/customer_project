# Generated by Django 5.1.3 on 2025-02-25 15:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0027_remove_reply_parent_comment_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentEditHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edited_at', models.DateTimeField(auto_now_add=True, help_text='The timestamp when the edit occurred.')),
                ('previous_file_name', models.CharField(blank=True, help_text='The previous file name (basename) of the document.', max_length=255)),
                ('previous_file_type', models.CharField(blank=True, choices=[('w9', 'W-9'), ('soil_test_result', 'Soil Test Result'), ('camp_registration', 'Camp Registration'), ('volunteer_registration', 'Volunteer Registration'), ('cover_crop_application', 'Cover Crop Application'), ('manure_application_record', 'Manure Application Record'), ('seed_tag', 'Seed Tag'), ('other', 'other'), ('lotl_registration', 'LOTL release form'), ('tree_sale_order_form', 'Tree Sale Order From'), ('fish_sale_order_form', 'Fish Sale Order From')], help_text='The previous file type of the document.', max_length=30)),
                ('previous_file_detail', models.CharField(blank=True, help_text='The previous description of the document.', max_length=100)),
                ('document', models.ForeignKey(help_text='The document that was edited.', on_delete=django.db.models.deletion.CASCADE, related_name='edit_history', to='customers.customerdocument')),
                ('edited_by', models.ForeignKey(blank=True, help_text='The user who made the edit.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='document_edits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-edited_at'],
            },
        ),
    ]
