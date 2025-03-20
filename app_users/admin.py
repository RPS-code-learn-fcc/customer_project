from django.contrib import admin

# Register your models here.

# get the CustomUser Model
from .models import CustomUser

# will allow for the creation of a custom admin interfase
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  

# creates the custom user admin interface
class CustomUserAdmin(BaseUserAdmin):  
   # Define the fields to display in the admin interface: admin/app_users/customuser/
   list_display = ('email', 'first_name', 'last_name', 'is_staff', 'last_login')  
   
   # define fields that CustomUsers can be filtered by
   list_filter = ('interests', 'job_title', 'email' )  
   
   # defines the sections for fields when editing CustomUser info
   fieldsets = (  
      (None, {'fields': ('email', 'password')}),  
      ('Personal Info', {'fields': ('first_name', 'last_name')}),
      ('Profile Info', {'fields': ('image', 'bio', 'job_title', 'interests')}), 
      ('Login Info', {'fields': ('date_joined', 'last_login', 'profile_updated')}),  
      ('Permissions', {'fields': ('is_staff', 'is_active', 'user_permissions')}),  

   )  
   # defines the fields for when the admin creates a new user
   add_fieldsets = (  
      (None, {  
        'classes': ('wide',),  
        'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),  
      }),  
   )  
   # defines the search fields that the admin can search by
   search_fields = ('email', 'first_name', 'last_name')
   
   # orders users by email  
   ordering = ('email',)  
   
   # sets certain fields as read-only as these should be automatically updated by the app & not edited
   readonly_fields = ('date_joined', 'last_login', 'profile_updated')

   # separate the many to many fields - available choices & chosen interests 
   filter_horizontal = ('interests', 'user_permissions')

  
admin.site.register(CustomUser, CustomUserAdmin)
