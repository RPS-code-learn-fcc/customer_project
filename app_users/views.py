from django.shortcuts import render, redirect, get_object_or_404

# import necessary forms and models
from .forms import EditCustomUserForm 
from .models import CustomUser

# imports exceptions from django's http module
from django.http import Http404, HttpResponseForbidden

# imports decorators to restrict certain views to logged in users, only
from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect


@login_required
def profile_view(request, email_prefix=None):
    """
        View to display a user profile.
        If an email prefix is given -> fetch that user's profile, else retrieve the logged in user's profile
    """
    # checks if an email prefix is provided; retrives user instance
    if email_prefix:
        userprofile = get_object_or_404(CustomUser, email__startswith=email_prefix)
    
    # else: retrieves the logged in user's profile
    else:
        try:
            # try to get the logged in user's information
            userprofile = request.user 
        
        # if the user's profile does not exist: 
        except CustomUser.DoesNotExist:
            raise Http404("User Profile Not Found.") # sends message that the user profile is not found
   
    # pass the context to the render a dynamic templage view
    context = {
        'profile': userprofile,
    }
    
    # pass on the template:
    template = 'app_users/view_userprofile.html'

    return render(request, template , context)

@login_required
def profile_edit_view(request, email_prefix):
    """
        View to edit a user profile.
        If an email prefix is given -> fetch that user's profile to populate the EditCustomUserForm
    """
    # checks if an email prefix is provided, that it belongs to the logged in user & retrieves the profile, if it exists
    if email_prefix and email_prefix == request.user.short_name():
        user = get_object_or_404(CustomUser, email__startswith=email_prefix)
    else:
        return HttpResponseForbidden("You do not have permission to edit this page.") # message displayed if the user is not the logged in user

    # Initialize the profile form with initial user data
    form = EditCustomUserForm(instance=user)
    
    # if it is a POST method: user entered data is passed to the form for validation
    if request.method == 'POST':
        # form includes data from HTTP POST request (data submitted by user, files and the user instance of the model that the form is editing
        form = EditCustomUserForm(request.POST, request.FILES, instance=user)

        # if the form is valid: the form is saved & the information entered by the user is added to the database
        if form.is_valid():
            form.save() # save the user instance which also calls the m2m save in the forms
            return redirect('userprofile-email', email_prefix=email_prefix)  # Redirect to profile view after saving profile data

    # pass context to the template to render a dynamic page
    context = {'form': form, 'profile': user}
    template = 'app_users/edit_userprofile.html'

    return render(request, template, context)



