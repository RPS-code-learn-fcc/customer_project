from django.db import models 

# AbstractBaseUser: base class for user model- provides fields password & last_login, behaves identically to default user model
# PermissionsMixin: adds permission-related fields and methods like: is_superuser
# Django's UserManager is given custom functionality
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

# imported to create timezone-aware dates & times
from django.utils import timezone
from django.utils.timesince import timesince


# provides an interface to access static files & file storage paths
from django.contrib.staticfiles.storage import staticfiles_storage

# import to perfrom regular expression validation, length validation validation & validation of the file extension of the image uploaded:
from django.core.validators import RegexValidator, MaxLengthValidator, FileExtensionValidator

# to resize image fields:
from django_resized import ResizedImageField

class CustomUserManager(UserManager):
    """ 
        Sets up a Custom User Manager to handle the creation of new users
    """
    # a private method to handle the creation of users
    def _create_user(self, email, password, **extra_fields):
        
        # an email must be provided or a value error
        if not email:
            raise ValueError("You must enter a valid email address.") # raised if email is None or Invalid
        
        # an entered email is converted to a normalized format: lowercase, etc.
        email = self.normalize_email(email)
        
        # a new user instance is created
        user = self.model(email=email, **extra_fields)
        
        # password is set and hashed
        user.set_password(password)
        
        # user is saved to the correct database
        user.save(using=self._db)
        
        return user

    # a public method for creating users
    def create_user(self, email=None, password=None, **extra_fields):
        
        # sets default values for certain fields for regular users
        extra_fields.setdefault('is_staff', False) # cannot access admin site
        extra_fields.setdefault('is_superuser', False) # is not a super user (has access to all permissions & admin site)
        
        # creates the user using the private method to follow DRY principles (can only be called within the manager)
        return self._create_user(email, password, **extra_fields)
     
    # public method for creating superusers
    def create_superuser(self, email=None, password=None, **extra_fields):
        # super users hava different default permissions that users
        extra_fields.setdefault('is_staff', True) # can access admin site
        extra_fields.setdefault('is_superuser', True) # has access to ALL permissions
        return self._create_user(email, password, **extra_fields)

# creates a CustomerUser class that extends the AbstractBaseUser and the PermissionsMixin   
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
        Creates a CustomUser Model with custom fields & uses an email for user authentication
    """
    # email required & cannot be blank
    email = models.EmailField(blank=False, unique=True)
    
    # first and last names can be blank as the email name contains the first and last name
    first_name = models.CharField(max_length=75, blank=True, validators=[ MaxLengthValidator(75), RegexValidator(regex=r'^[a-zA-Z0-9\s-]+$', message="Name can only contain letters, numbers and dashes.")])
    last_name = models.CharField(max_length=75, blank=True, validators=[ MaxLengthValidator(75), RegexValidator(regex=r'^[a-zA-Z\s-]+$', message="Name can only contain letters and dashes.")])

    # set permissions
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    # keep track of when users joined / logged in: built-in
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # add another field to keep track of when the profile was most recently updated
    profile_updated = models.DateTimeField(blank=True, null=True)
    
    # set other custom user fields (all optional w/defaults provided):
    image = ResizedImageField(size=[600,600], quality=85, upload_to='profile_images/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])], blank=True) # optional - only allow jpgs
    bio = models.TextField(null=True, blank=True, default="The lack of power to take joy in outdoor nature is as real a misfortune as the lack of power to take joy in books. --T. Roosevelt.", validators=[ MaxLengthValidator(500), RegexValidator(regex=r'^[a-zA-Z0-9\s.!?,-:;]+$', message="Only letters, numbers, spaces, and common punctuation are allowed. Max 500 characters.")])
    job_title = models.CharField(max_length=75, null=True, blank=True, default='Conservation Specialist', validators=[ MaxLengthValidator(50), RegexValidator(regex=r'^[a-zA-Z\s-]+$', message="Job Description can only contain letters and dashes.")])
    
    # add interests for the user (from the other app - customers):
    interests = models.ManyToManyField(
        'customers.CustomerInterest',
        blank=True,
        related_name="users_with_interest",  # Reverse relationship name
        help_text="Select your interests"
    )
    
    # verrides the default 'objects' that comes with django
    objects = CustomUserManager() 
    
    # email takes the place of 'username' and to user email field for this
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = [] # additional required fields when creating a superuser
    
    # sets the name of the users on the admin panel
    class Meta: 
        verbose_name = 'CompanyUser'
        verbose_name_plural = 'CompanyUsers'
    
    def get_full_name(self):
        """Returns the First and Last Name of User"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def short_name(self):
        """Returns the email prefix of user: example@email.com returns 'example'"""
        return self.email.split('@')[0]
    
    # add properties: these are like fields but come from model data - allows for dynamic interactions
    @property 
    def profile_image(self):
        """Returns the URL of the associated profile image - if it exists - OR a default profile image"""
        try:
            profile_image = self.image.url # URL of the associated profile image
        except ValueError:  # ValueError Raised if `image` is None or invalid
            return staticfiles_storage.url('images/default_profile_image.jpg') # gets default profile image
        return profile_image
    
    @property
    def user_name(self):
        """Returns the full name of the user - if it exists - OR returns the shortened user name: the email prefix"""
        
        # Uses the built-in method to get the user's full name
        full_name = self.get_full_name()  
        
        # returns the full name if it exists
        if full_name:  
            return full_name
        
        # else it returns the shortened email as email is required to login / create a user
        return self.short_name()  
    
    @property
    def time_since_joined(self):
        """Returns how long a user has been a registered user"""
        return timesince(self.date_joined)

