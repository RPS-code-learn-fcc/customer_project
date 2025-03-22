from django.db import models
import os
from app_users.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils import timezone

from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

# provides an interface to access static files & file storage paths
from django.conf import settings
from django.core.files.storage import default_storage


def validate_file_type(value):
    """
    Validator to ensure only PDFs and Word documents are uploaded.
    """
    valid_extensions = ['.pdf', '.doc', '.docx']
    ext = os.path.splitext(value.name)[1].lower()  # Get file extension
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file type: {ext}. Only PDF and Word documents are allowed.")

class CustomerDocument(models.Model):
    """
        Allows for the Linking of Multiple Documents to Individual Customers
    """
    # defines the file
    file = models.FileField(upload_to="customer_documents/", blank=False, validators=[validate_file_type],)
    
    # File type options
    FILE_TYPES = [
            ('w9', 'W-9'),
            ('soil_test_result', 'Soil Test Result'),
            ('camp_registration', 'Camp Registration'),
            ('volunteer_registration', 'Volunteer Registration'),
            ('cover_crop_application', 'Cover Crop Application'),
            ('manure_application_record', 'Manure Application Record'),
            ('seed_tag', 'Seed Tag'),
            ('other', 'other'),
            ('lotl_registration', 'LOTL release form'),
            ('tree_sale_order_form', 'Tree Sale Order From'),
            ('fish_sale_order_form', 'Fish Sale Order From'),
        ]

    # Field to store the selected file type
    file_type = models.CharField(max_length=30, choices=FILE_TYPES, blank=True, help_text="Select the file type")
    
    # allows for an optional description of the file
    file_detail = models.CharField(max_length=100, blank=True, help_text="Optional description of file material.")
    
    # keeps track of who uploaded the file
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='author_document') # if the CustomUser is deleted -> author is set to null 

    # creates a timestamp for when the document was uploaded
    created_at = models.DateTimeField(auto_now_add=True)
    
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name="documents")
    
    def clean(self):
        super().clean()
        # If file_type is 'other', ensure that file_detail is provided.
        if self.file_type == 'other' and not self.file_detail.strip():
            raise ValidationError({
                'file_detail': "You must provide a file detail when the file type is set to 'other'."
            })


    def __str__(self):  
        """
            Returns the File Name & Description or just the file name, both have the timestamp
        """
        file_name = os.path.basename(self.file.name)  # Extract just the file name
        if self.file_detail:  
            return f'{file_name} - Desc: {self.file_detail}'  
        else:  
            return f'{file_name}'
        
    def save(self, *args, **kwargs):
        """Custom save method to update the file name of the file uploaded"""
        if self.file:
            file_type = dict(self.FILE_TYPES).get(self.file_type, "")
            customer_name = self.customer.display_name
            year = timezone.now().year
            new_file_name = f"{customer_name}_{file_type}_{year}.pdf"
            self.file.name = new_file_name
        super().save(*args, **kwargs)
        
    class Meta:
        # order so that the most recent customer created is shown first
        ordering = ['-created_at']


class CustomerNote(models.Model):
    """
        Allows for the Linking of Multiple Notes to Individual Customers
    """
    
    # the customer note
    note = models.TextField(blank=True)
    
    # timestamp for when the note is created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # tracks which user created the note
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='author_notes') # if the CustomUser is deleted -> author is set to null 

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name="notes")

    
    def __str__(self):  
        return f'{self.note[:30]}... ({self.created_at.strftime("%B %d, %Y, %I:%M %p")})'
    
    class Meta:
        # order so that the most recent customer created is shown first
        ordering = ['-created_at']
        
    @property
    def note_number(self):
        return CustomerNote.objects.filter(customer=self.customer, id__lte=self.id).count()
        
class CustomerInterest(models.Model):
    """
        Tracks the Interests of Customers 
    """
    
    # Name of the interest ("Tree Sale", "Soil Tests", etc.)
    name = models.CharField(max_length=50, unique=True, validators=[MinLengthValidator(4), MaxLengthValidator(50), RegexValidator(regex=r'^[a-zA-Z0-9\s-]+$', message="Name can only contain letters, spaces, numbers and dashes.")])
    
    # optional image - icon associated with the interest
    icon_image = models.FileField(upload_to='icons/', null=True, blank=True)
    
    # slug
    slug = models.SlugField(max_length=20, unique=True, validators=[MinLengthValidator(4), MaxLengthValidator(20), RegexValidator(regex=r'^[a-zA-Z0-9-]+$', message="Name can only contain letters, numbers and dashes.")]) # string we use in the address bar
        
    def __str__(self):
        return str(self.name)
    
    class Meta: 
        ordering = ['name']
        
    @property
    def icon_image_url(self):
        """
        Returns the URL of the associated icon image if it exists,
        otherwise returns the default star image URL from settings.
        """
        if self.icon_image:  # Check if the icon_image exists
            return self.icon_image.url  # Return the URL of the associated icon
        else:
            # Return the default star image URL from settings
            return settings.DEFAULT_STAR_IMAGE_URL

class CustomerMailingList(models.Model):
    """Creates a mailing list based on interests"""
    name = models.CharField(max_length=255, unique=True, validators=[MinLengthValidator(4), MaxLengthValidator(50), RegexValidator(regex=r'^[a-zA-Z0-9\s-]+$', message="Name can only contain letters, spaces, numbers and dashes.")], help_text="Mailing List Name: 'Fish Sale', 'Summer Camp' (if based on an interest) or a custom name")
    customers = models.ManyToManyField('Customer', related_name="mailing_lists", blank=True)
    addresses = models.ManyToManyField('Address', related_name="mailing_addresses", blank=True)
    interests = models.ManyToManyField('CustomerInterest', related_name="mailing_interests", blank=True)
    
    # creates a timestamp for when the mailing list was created
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    
    class Meta: 
        ordering = ['-created_at']
    
class CustomerNoteHistory(models.Model):
    """Stores the edit history of CustomerNotes"""
    customer_note = models.ForeignKey(CustomerNote, on_delete=models.SET_NULL, related_name="note_history", null=True)
    previous_note = models.TextField()
    edited_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='edit_authors') # if the CustomUser is deleted -> author is set to null 
    edited_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.customer_note} was last edited by {self.edited_by} at {self.edited_at.strftime("%B %d, %Y, %I:%M %p")}'

class CustomerDocumentHistory(models.Model):
    """
    Tracks changes made to a CustomerDocument.
    """
    document = models.ForeignKey(
        'CustomerDocument',
        on_delete=models.CASCADE,
        related_name='edit_history',
        help_text="The document that was edited."
    )
    edited_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The timestamp when the edit occurred."
    )
    edited_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_edits',
        help_text="The user who made the edit."
    )
    previous_file_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="The previous file name (basename) of the document."
    )
    previous_file_type = models.CharField(
        max_length=30,
        choices=CustomerDocument.FILE_TYPES,
        blank=True,
        help_text="The previous file type of the document."
    )
    previous_file_detail = models.CharField(
        max_length=100,
        blank=True,
        help_text="The previous description of the document."
    )

    def __str__(self):
        return f"Edit on {self.document} at {self.edited_at}"
    
    def save(self, *args, **kwargs):
        """Handles the absence of any file description upon saving"""
        if not self.previous_file_detail:
            self.previous_file_detail = "No description provided"
        super().save(*args, **kwargs)


    class Meta:
        ordering = ['-edited_at']

