from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.core.exceptions import ValidationError

class Address(models.Model):
    """
        Addresses of Customers: street (optional), city (required), state (required), zip code 
    """
    STATE_CHOICES = [
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming'),
]

    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    zip_code = models.CharField(
        max_length=5,
        validators=[
            MinLengthValidator(5),
            MaxLengthValidator(5),
            RegexValidator(regex=r'^\d{5}$', message='Zip code can only contain 5 numbers.')
        ],
        blank=False,
        null=False)
    mailing_address = models.BooleanField(default=True)
    
    def clean(self):
 # Ensure that a mailing address must have a street
        if not self.street and self.mailing_address:
            raise ValidationError("A mailing address must have a street. Either provide a street or unselect 'Mailing Address'.")
  
    def __str__(self):
        address_type = "Mailing Address" if self.mailing_address else "Do Not Send Mail"  
        street = f"{self.street}, " if self.street else " "  
        return f"{address_type}: {street}{self.city}, {self.state} {self.zip_code}"

class Email(models.Model):
    """
        Email of Customers: Email is required and it is automatically set as a default email, other fields: type of email, etc. are not
    """
    email_address = models.EmailField(blank=False, null=False)
    EMAIL_TYPE_CHOICES = {
    "home": "HOME",
    "work": "WORK",
    "farm": "FARM",
    }
    email_type = models.CharField(max_length=4, choices=EMAIL_TYPE_CHOICES, blank=True, null=True)
    preferred_email = models.BooleanField(default=True)
   
    
    def __str__(self):
        email_type_display = f" ({self.email_type})" if self.email_type else ""
        return f'{self.email_address or "No Email Provided"}{email_type_display}'

class Phone(models.Model):
    phone_number = models.CharField(
        max_length=15,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$|^\d{3}-\d{3}-\d{4}$',
                message='Phone number must be in the format 3306742811 or 330-674-2811.'
            )
        ]
    )
    extension = models.CharField(
        max_length=5,
        blank=True,
        null= True,
        validators=[
            RegexValidator(
                regex=r'^\d*$',
                message='Only numbers are allowed for the extension.'
            )
        ]
    )
    PHONE_TYPE_CHOICES = {
        "cell": "CELL",
        "home": "HOME",
        "work": "WORK",
        "farm": "FARM",
    }

    phone_type = models.CharField(max_length=4, choices=PHONE_TYPE_CHOICES)
    can_call = models.BooleanField(default=True)
    can_text = models.BooleanField(default=True)
    can_leave_voicemail = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=True)
    def __str__(self):  
        ext = f" ext:{self.extension}" if self.extension else ""  
        phone_type = f" ({self.get_phone_type_display()})" if self.phone_type else ""  
        return f"{self.phone_number}{ext}{phone_type}"
    
    def save(self, *args, **kwargs):
        # Standardize the phone number format to `330-674-2811`
        if self.phone_number:
            # Remove all non-digit characters
            digits_only = ''.join(filter(str.isdigit, self.phone_number))
            
            # Format if it has 10 digits
            if len(digits_only) == 10:
                self.phone_number = f"{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
        
        super().save(*args, **kwargs)

class ContactMethod(models.Model):
    """
        Represents a Preferred Contact Method: phone, text, email, text, etc.
    """
    method_name = models.CharField(max_length=20, unique=True, help_text="Preferred Contact Method: phone, email, text, voicemail, etc.")
    
    def __str__(self):
        return str(self.method_name)
    

