from django.db import models
from django.core.validators import ValidationError
from app_users.models import CustomUser


class Customer(models.Model):
    """
        Represents a generic Customer, which could be a Person, Farm, Business, Organization, etc.
    """
    CUSTOMER_CHOICES = [
        ("person", "Person"),
        ("farm", "Farm"),
        ("business", "Business"),
        ("organization", "Organization"),
        ("government", "Government"),
    ]

    first_name = models.CharField(max_length=75, blank=False, help_text="If a person enter both a first & last name - if a business, etc. leave last name blank.")
    last_name = models.CharField(max_length=75, blank=True)
    customer_type = models.CharField(max_length=12, choices=CUSTOMER_CHOICES, blank=False)

    # Self-referential relationship for linking customers
    related_customers = models.ManyToManyField(
        'self', 
        through='CustomerRelationship', 
        symmetrical=False, 
        related_name='linked_customers',
        blank=True
    )
    
    # Many to many Relationships:
    # Many-to-Many field for preferred contact methods
    preferred_contact_methods = models.ManyToManyField(
        'ContactMethod', 
        blank=True, 
        related_name='customers_preferred_contact_methods', 
        help_text="Customer's preferred method(s) of contact"
    )
        
                
    # Many-to-Many field for Associated Customer Interests 
    interests = models.ManyToManyField('CustomerInterest', blank=True, related_name="customer_interests")
    
    # Many-to-Many field for Associated Customer Addresses 
    addresses = models.ManyToManyField('Address', blank=True, related_name="customer_addresses")
    
    # Many-to-Many field for Associated Customer phone numbers
    phones = models.ManyToManyField('Phone', blank=True, related_name="customer_phones")
    
    # Many-to-Many field for Associated Customer emails 
    emails = models.ManyToManyField('Email', blank=True, related_name="customer_emails")
        
    # Keep track of when a customer is added to the datbase
    created_at = models.DateTimeField(auto_now_add=True)
    
    # mark when a customer is active or not (only displayed when updating a customer profile)
    is_inactive = models.BooleanField(default=False, help_text="Mark Inactive if Customer has moved, is deceased, etc.")

    # keeps track of who creates the customer
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='creator_customer') # if the CustomUser is deleted -> author is set to null 
    
    def clean(self):
        """
            Validation: Ensure both first and last name fields are provided for a customer of type "person".
        """
        if self.customer_type == "person":
            # Check if both first_name and last_name are provided
            if not self.first_name:
                raise ValidationError("A Person must have a first name.")
            if not self.last_name:
                raise ValidationError("A Person must have a last name.")
            
        else:
            # Check that a first name is only entered for non-person entities
            if self.last_name:
                raise ValidationError("For non-person entities, please do not include a last name. Add a First Name, only.")


    def __str__(self):
        """
            Return customer names and entity type if not a person.
        """
        if self.customer_type == "person":
            return f"{self.first_name} {self.last_name}".strip()
        return f"{self.first_name} ({self.customer_type.capitalize()})"

    class Meta:
        # order so that the most recent customer created is shown first
        ordering = ['-created_at']
    
    @property  
    def display_name(self):  
        """  
         Returns the display name for the customer based on their customer type.  
        """  
        if self.customer_type == "person":  
            return f"{self.first_name} {self.last_name}".strip()  
        else:  
            return f"{self.first_name} ({self.customer_type})" 
        
    @property  
    def mailing_list_name(self):  
        """  
         Returns the mailing list name for the customer based on their customer type.  
        """  
        if self.customer_type == "person":  
            return f"{self.first_name} {self.last_name}".strip()  
        else:  
            return f"{self.first_name}" 
        
    @property  
    def preferred_contact_methods_display(self):  
        """  
            Returns a string representation of the customer's preferred contact methods.  
        """  
        # queries db for all methods 
        methods = self.preferred_contact_methods.all()  
        
        # if the method exists list them all
        if methods:  
            return ', '.join([method.method_name for method in methods])  
        # else send a string method
        else:  
            return 'No preferred contact method.'
    
    @property  
    def has_primary_phone(self):  
        """  
            Returns True if the customer has a primary phone number, False otherwise.  
        """  
        return self.phones.filter(is_primary=True).exists()  
    
    @property  
    def primary_phone_details(self):  
        """  
        Returns the primary phone number, phone type, and count of primary phone numbers.  
        """  
        primary_phones = self.phones.filter(is_primary=True)  
        if primary_phones.exists():  
            return f"{primary_phones.first().phone_number} ({primary_phones.first().phone_type}) - ({primary_phones.count()} phone number{'' if primary_phones.count() == 1 else 's'})"  
        else:  
            return 'No primary phone number.'
            
    @property  
    def preferred_email(self):  
        """  
            Returns the preferred email of the customer, if it exists.  
        """  
        preferred_email = self.emails.filter(preferred_email=True)  
        if preferred_email.exists():  
            return f"{preferred_email.first().email_address } ({preferred_email.first().email_type})" 
        else:  
            return 'No preferred email.'
        

    @property  
    def email_count(self):  
        """  
            Returns the  number of emails.  
        """  
        emails = self.emails.count()  
        if emails:  
            return f"{emails} email{'' if emails == 1 else 's'}"  
        else:  
            return '0 emails'
        
    
    @property  
    def mailing_address(self):  
        """  
            Returns the mailing address of the customer, if it exists.  
        """  
        mailing_address = self.addresses.filter(mailing_address=True)  
        if mailing_address.exists():  
            return f"{mailing_address.first().street} {mailing_address.first().city }, {mailing_address.first().state } {mailing_address.first().zip_code }" 
        else:  
            return 'No mailing address.'
    
    @property
    def address_count(self):
        """
        Returns the number of addresses for the customer.
        """
        addresses = self.addresses.count()
        if addresses == 1:
            return f"{addresses} address"
        elif addresses > 1:
            return f"{addresses} addresses"
        else:
            return "0 addresses"
    
    @property  
    def phone_count(self):  
        """  
            Returns the  number of phone numbers for the customer.  
        """  
        phones = self.phones.count()  
        if phones:  
            return f"{phones} phone number{'' if phones == 1 else 's'}"  
        else:  
            return f"0 phone numbers" 


class CustomerRelationship(models.Model):
    """
        Links one Customer to another via a defined relationship: owner, employee, etc. Multiple relationship types are possible for one customer.
    """
    
    # types of relationships available between customers
    RELATIONSHIP_TYPES = [
        ("owner", "Owner of"),
        ("employee", "Employee of"),
        ("partner", "Partner with"),
        ("linked", "Linked to"),
        ("volunteer", "Volunteer of"),
        ("spouse", "Spouse of")

    ]

    # customer that "initiates the relationship"
    from_customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='from_relationships'
    )
    
    # customer that the relationship is to
    to_customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='to_relationships'
    )
    
    # select the relationship type
    relationship_type = models.CharField(
        max_length=20, 
        choices=RELATIONSHIP_TYPES, 
        blank=False
    )
    
    # add a timestamp for when the relationship is created
    created_at = models.DateTimeField(auto_now_add=True)
  

    def __str__(self):
        return f"{self.from_customer} ({self.relationship_type}) {self.to_customer}"
