from django import forms # imports entire djanto forms module: form, ModelForm, FormSet, ValidationError

# imports the CustomUser model that I created
from .models import CustomUser

# imported to create timezone-aware dates & times
from django.utils import timezone


class EditCustomUserForm(forms.ModelForm):
    """
        A form that lets logged in users edit specified fields: image, bio, job_title & interests
    """
    class Meta:
        """          
            model (Model): The model associated with this form.  
            fields (tuple): A list of field names to include in the form.  
            widgets (dict): A dictionary of widgets to use for each field.  
        """  
        model = CustomUser  # this form works with this model
        fields = [ 'image', 'bio', 'job_title', 'interests']  # only these fields are editable
        
        # how the form fields are displayed on the page
        widgets = {  
            'bio': forms.Textarea(attrs={'rows': 3}), # a 3 line text box is displayed
            'image': forms.FileInput(attrs={'class': 'file-input'}),  # only a FileInput is shown -> to upload a new image & a css class is added
            'interests': forms.CheckboxSelectMultiple(attrs={'class':'checkbox-buttons'}),  # interests will be checkboxes with css class: checkbox-buttons that allows them to be styled like buttons

        }
        labels = {  
            # gives more user friendly labels for certain fields
            'image': 'Upload New Profile Image',  
            'bio': 'Quote or My Bio:',  
            'interests': 'Select your Interests:'
        }
    def __init__(self, *args, **kwargs):  
        """ Initializes the form instance."""
        super().__init__(*args, **kwargs)  
        self.fields['interests'].help_text = '' # when defining the form field -> the help text for interests is set to an empty string
      
    def save(self, commit=True):
        """On saving the form - the profile_updated time is set to the current time and .save_m2m() is called to save many to many relastionships. It returns the user instance"""
        user = super().save(commit=False) # save the user but don't yet commit to the database
        user.profile_updated = timezone.now() # gets current time
        if commit:
            user.save() # save the user to the database
            self.save_m2m() # save many to many fields (interests) to the database
        return user
    
