
from django.forms import ModelForm


from django import forms
from .models import * 
from .models import CustomerMailingList, CustomerNoteHistory, CustomerDocumentHistory
from django.urls import reverse

class CreateCustomerForm(ModelForm):  
   class Meta:  
        model = Customer  
        street = forms.CharField(max_length=255)
        fields = ['first_name', 'last_name', 'customer_type', 'preferred_contact_methods', 'interests']
        labels = { 
                'first_name': 'First Name or Name', 
                'preferred_contact_methods': 'Preferred method(s) of contact:',
                'customer_type': 'Choose Customer Type',
                'interests': 'Add Customer to the Following Mailing Lists (if interests exist):'
                }  
        widgets = {  
        'customer_type': forms.Select(attrs={'style': 'width: 80%;'}),  
        'preferred_contact_methods': forms.CheckboxSelectMultiple(attrs={'class':'checkbox-buttons'}),  
        'interests': forms.CheckboxSelectMultiple(attrs={'class':'checkbox-buttons'}),  

        }  
        def __init__(self, *args, **kwargs):
            """set initial form values based on the instance being edited."""
            super(CreateCustomerForm, self).__init__(*args, **kwargs)
            if self.instance:
                self.fields['first_name'].initial = self.instance.first_name
                self.fields['last_name'].initial = self.instance.last_name
                self.fields['customer_type'].initial = self.instance.customer_type
                self.fields['preferred_contact_methods'].initial = self.instance.preferred_contact_methods.all()
                self.fields['interests'].initial = self.instance.interests.all()

class CreateAddressForm(ModelForm):
    class Meta:
        model = Address
        fields = "__all__"
        widgets = {  
            'mailing_address': forms.CheckboxInput(attrs={'class':'custom-checkbox', }),  
            'street': forms.TextInput(attrs={'placeholder': 'Enter street address', 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter city', 'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-select', 'style': 'width: 80%;'}),
            'zip_code': forms.TextInput(attrs={'placeholder': 'Enter ZIP code', 'class': 'form-control'}),
        }  
   
    
class CreatePhoneForm(ModelForm):
    class Meta:
        model = Phone
        fields = "__all__"
        labels = { 
                'is_primary': 'Primary Phone Number', 
                'can_call': 'Can Call',
                'can_text': 'Can Text',
                'can_leave_voicemail': 'Leave Voicemail',
            }  
        widgets = {  
            'is_primary': forms.CheckboxInput(attrs={'class':'custom-checkbox', }), 
            'can_call': forms.CheckboxInput(attrs={'class':'custom-checkbox', }),  
            'can_text': forms.CheckboxInput(attrs={'class':'custom-checkbox', }),  
            'can_leave_voicemail': forms.CheckboxInput(attrs={'class':'custom-checkbox', }),  
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter email address', 'class': 'form-control'}),
            'extension': forms.TextInput(attrs={'placeholder': 'Enter email address', 'class': 'form-control'}),
            'phone_type': forms.Select(attrs={'class': 'form-select', 'style': 'width: 80%;'}),
        }  
        
class CreateEmailForm(ModelForm):
    class Meta:
        model = Email
        fields = "__all__"
        labels = { 
                'preferred_email': 'Primary Email', 
                'email_address': 'Email Address',
                'email_type': 'Choose Email Type',
            }  
        widgets = {  
            'preferred_email': forms.CheckboxInput(attrs={'class':'custom-checkbox', }),  
            'email_address': forms.TextInput(attrs={'placeholder': 'Enter email address', 'class': 'form-control'}),
            'email_type': forms.Select(attrs={'class': 'form-select', 'style': 'width: 80%;'}),
        }  
        
class CreateDocumentForm(forms.ModelForm):
    class Meta:
        model = CustomerDocument
        exclude = ['author', 'created_at', 'customer']
        labels = { 
            'file': '', 
            'File Detail': 'Add a description',
        }  

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        if not file:
            raise forms.ValidationError('A File is required')
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None) # get user from view
        super().__init__(*args, **kwargs)
        # save the history of the document edit if the new version is NOT equal to the old version of the note    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if instance.pk:
            original_instance = CustomerDocument.objects.get(pk=instance.pk)
            # Check if any of the document fields have changed
            if (original_instance.file != instance.file or
                original_instance.file_type != instance.file_type or
                original_instance.file_detail != instance.file_detail):
                CustomerDocumentHistory.objects.create(
                    document=instance,
                    previous_file_name=original_instance.file,
                    previous_file_type=original_instance.file_type,
                    previous_file_detail=original_instance.file_detail,
                    edited_by=self.request_user
                )
        if commit:
            instance.save()
        return instance

class CreateNoteForm(ModelForm):
    class Meta:
        model = CustomerNote
        exclude = ['author', 'created_at', 'customer']
        labels = { 
                'note': 'Add a Note', 
            }  
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None) # get user from view
        super().__init__(*args, **kwargs)
    
    # save the history of the note edit if the new version is NOT equal to the old version of the note    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if instance.pk:
            original_instance = CustomerNote.objects.get(pk=instance.pk)
            if original_instance.note != instance.note:
                CustomerNoteHistory.objects.create(
                    customer_note =instance,
                    previous_note = original_instance.note,
                    edited_by = self.request_user
                )
        if commit:
            instance.save()
        return instance
    

class CreateCustomerInterest(ModelForm):
    class Meta:
        model = CustomerInterest
        exclude = ['slug']
        labels = { 
                'icon_image': 'Icon (optional)', 
            }  
        
class CreateCustomerContactMethod(ModelForm):
    class Meta:
        model = ContactMethod
        fields = '__all__'

class CreateCustomerMailingListForm(ModelForm):
    class Meta:
  
        model = CustomerMailingList
        fields = ['interests', 'name']
        widgets = {  
            'interests': forms.CheckboxSelectMultiple(attrs={'class':'checkbox-buttons'}),  
            'name': forms.TextInput(attrs={'placeholder': 'Tree Sale',}),

        }

# Form for toggling the is_inactive field
class ToggleInactiveForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['is_inactive']
        
