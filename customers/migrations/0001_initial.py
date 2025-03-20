# Generated by Django 5.1.3 on 2024-12-31 21:38

import customers.models.relationships
import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], max_length=2)),
                ('zip_code', models.CharField(max_length=5, validators=[django.core.validators.MinLengthValidator(5), django.core.validators.MaxLengthValidator(5), django.core.validators.RegexValidator(message='Zip code can only contain 5  numbers.', regex='^\\d{5}$')])),
                ('mailing_address', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContactMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method_name', models.CharField(help_text='Preferred Contact Method: phone, email, text, voicemail, etc.', max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerInterest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('image', models.FileField(blank=True, null=True, upload_to='icons/')),
                ('slug', models.SlugField(max_length=20, unique=True)),
                ('order', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_address', models.EmailField(max_length=254)),
                ('email_type', models.CharField(blank=True, choices=[('home', 'HOME'), ('work', 'WORK'), ('farm', 'FARM')], max_length=4, null=True)),
                ('preferred_email', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be in the format 3306742811 or 330-674-2811.', regex='^\\d{10}$|^\\d{3}-\\d{3}-\\d{4}$')])),
                ('extension', models.CharField(blank=True, max_length=5, null=True, validators=[django.core.validators.RegexValidator(message='Only numbers are allowed for the extension.', regex='^\\d*$')])),
                ('phone_type', models.CharField(choices=[('cell', 'CELL'), ('home', 'HOME'), ('work', 'WORK'), ('farm', 'FARM')], max_length=4)),
                ('can_call', models.BooleanField(default=True)),
                ('can_text', models.BooleanField(default=True)),
                ('can_leave_voicemail', models.BooleanField(default=True)),
                ('is_primary', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='If a person enter both a first & last name - if a business, etc. leave last name blank.', max_length=75)),
                ('last_name', models.CharField(blank=True, max_length=75)),
                ('customer_type', models.CharField(choices=[('person', 'Person'), ('farm', 'Farm'), ('business', 'Business'), ('organization', 'Organization'), ('government', 'Government')], max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_inactive', models.BooleanField(default=False, help_text='Mark Inactive if Customer has moved, is deceased, etc.')),
                ('addresses', models.ManyToManyField(blank=True, related_name='customer_addresses', to='customers.address')),
                ('emails', models.ManyToManyField(blank=True, related_name='customer_emails', to='customers.address')),
                ('phones', models.ManyToManyField(blank=True, related_name='customer_phones', to='customers.address')),
                ('preferred_contact_methods', models.ManyToManyField(blank=True, help_text="Customer's preferred method(s) of contact", related_name='customers_preferred_contact_methods', to='customers.contactmethod')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('body', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('commented_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='customers.customer')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomerDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, upload_to='customer_documents/', validators=[customers.models.relationships.validate_file_type])),
                ('file_detail', models.CharField(blank=True, help_text='Optional description of file material.', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_document', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='documents',
            field=models.ManyToManyField(blank=True, help_text='Add a Document', related_name='customer_documents', to='customers.customerdocument'),
        ),
        migrations.AddField(
            model_name='customer',
            name='interests',
            field=models.ManyToManyField(blank=True, related_name='customer_interests', to='customers.customerinterest'),
        ),
        migrations.CreateModel(
            name='CustomerNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_notes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='notes',
            field=models.ManyToManyField(blank=True, related_name='customer_notes', to='customers.customernote'),
        ),
        migrations.CreateModel(
            name='CustomerRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_type', models.CharField(choices=[('owner', 'Owner of'), ('employee', 'Employee of'), ('partner', 'Partner with'), ('linked', 'Linked to'), ('volunteer', 'Volunteer of'), ('spouse', 'Spouse of')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_relationships', to='customers.customer')),
                ('to_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_relationships', to='customers.customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='related_customers',
            field=models.ManyToManyField(blank=True, related_name='linked_customers', through='customers.CustomerRelationship', to='customers.customer'),
        ),
        migrations.CreateModel(
            name='LikedComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.comment')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='likes',
            field=models.ManyToManyField(related_name='likedcomments', through='customers.LikedComment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='LikedCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='likes',
            field=models.ManyToManyField(related_name='liked_data', through='customers.LikedCustomer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='LikedReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('CustomUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('body', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(related_name='likedreplies', through='customers.LikedReply', to=settings.AUTH_USER_MODEL)),
                ('parent_comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='customers.comment')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.AddField(
            model_name='likedreply',
            name='reply',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.reply'),
        ),
    ]
