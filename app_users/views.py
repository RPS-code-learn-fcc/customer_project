from django.shortcuts import render, redirect, get_object_or_404

# import necessary forms and models
from .forms import EditCustomUserForm 
from .models import CustomUser

# imports exceptions from django's http module
from django.http import Http404, HttpResponseForbidden

# imports decorators to restrict certain views to logged in users, only
from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect

# to create a digraph diagram of the custom user model
from django.http import HttpResponse
from graphviz import Digraph

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

def custom_user_model_structure_view(request):
    """View that creates a diagram of the Custom User model & its fields"""
    dot = Digraph(format='png')
    
    # Enhanced rendering settings
    dot.attr(
        rankdir='TB',
        size='8,10',
        dpi='300',
        fontname='Arial',
        fontsize='16',
        labelloc='t',
        label='CustomUser Model: Structure & Fields',
        pad='0.5',
        nodesep='0.25',
        ranksep='0.4'
    )
    
    # Node styling
    node_attrs = {
        'fontname': 'Arial',
        'fontsize': '16',
        'shape': 'box',
        'style': 'filled,rounded',
        'margin': '0.15,0.1'
    }

    # Basic Model info
    dot.node('core', '''CustomUser Model Core
──────────────────────
Inheritance:
• AbstractBaseUser
• PermissionsMixin

Authentication:
• USERNAME_FIELD: email
• EMAIL_FIELD: email
• REQUIRED_FIELDS: []''',
             **node_attrs, fillcolor='#f0f8ff')

    # clusters for fields
    with dot.subgraph(name='cluster_auth') as c:
        c.attr(style='filled,rounded',
               label='Authentication',
               fillcolor='#e6f3ff',
               fontsize='11')
        c.node('email', 'email\n(EmailField)\n• Required\n• Unique', **node_attrs)
        c.node('pw', 'password\n(AbstractBaseUser)', **node_attrs)
        c.node('perms', '''Permissions:
• is_active
• is_staff
• is_superuser''', **node_attrs)

    with dot.subgraph(name='cluster_profile') as c:
        c.attr(style='filled,rounded',
               label='Profile Data',
               fillcolor='#e8f5e9',
               fontsize='11')
        c.node('names', '''Names:
• first_name (75 chars)
• last_name (75 chars)''', **node_attrs)
        c.node('image', '''image (ResizedImageField):
• 600x600px
• JPG/JPEG only''', **node_attrs)
        c.node('bio', '''bio (TextField):
• 500 chars max
• Validated content''', **node_attrs)
        c.node('job', '''job_title:
• 50 chars max
• Letters/dashes only''', **node_attrs)

    with dot.subgraph(name='cluster_relations') as c:
        c.attr(style='filled,rounded',
               label='Relationships',
               fillcolor='#fff3e0',
               fontsize='11')
        c.node('interests', '''interests (M2M):
→ CustomerInterest
• Blank=True''', **node_attrs)

    with dot.subgraph(name='cluster_time') as c:
        c.attr(style='filled,rounded',
               label='Timestamps',
               fillcolor='#f5f5f5',
               fontsize='11')
        c.node('timestamps', '''• date_joined
• last_login
• profile_updated''', **node_attrs)

    # -- connect the nodes ------
    dot.edge('core', 'cluster_auth')
    dot.edge('core', 'cluster_profile')
    dot.edge('core', 'cluster_relations')
    dot.edge('core', 'cluster_time')

    # try / catch block for generating the image
    try:
        png_data = dot.pipe(engine='dot', format='png')
        return HttpResponse(png_data, content_type='image/png')
    except Exception as e:
        return HttpResponse(f"Diagram Error: {str(e)}", status=500)

def custom_user_methods_view(request):
    """Creates a diagram of the Custom User Model Methods: Manager, Instance, Properties & validation"""
    dot = Digraph(format='png')
    
    # Make the diagram easier to read
    # can see the text better in a large diagram
    dot.attr(
        rankdir='TB', # top to bottom orientation
        size='10,10',
        dpi='300', # high-resolution
        fontname='Arial',
        fontsize='16',
        labelloc='t',
        label='CustomUser: Manager & Methods',
        pad='0.75',
        nodesep='0.25', # min space between sibling nodes
        ranksep='0.4' # min space between hierch. labels
    )

    # Node styling: sets margins & padding, shape of noes
    method_node_attrs = {
        'fontname': 'Arial',
        'fontsize': '16',
        'shape': 'box',
        'style': 'filled,rounded',
        'margin': '0.15,0.1', 
        'align': 'center'
    }
    

    # ----------- Explains the Custom User Manager -----------------
    with dot.subgraph(name='cluster_manager') as c:
        # sets styling of this node
        c.attr(style='filled,rounded',
               label='CustomUserManager',
               fillcolor='#fff3e0',
               fontsize='16')
        
        c.node('mgr', 'Manager Methods\n─────────────────', **method_node_attrs) # applies styles
        c.node('private', '''_create_user():
                1. Validate email
                2. Normalize email
                3. Set password
                4. Save to database''', **method_node_attrs)
        c.node('create', '''create_user():
                • Sets defaults:
                - is_staff=False
                - is_superuser=False''', **method_node_attrs)
        c.node('super', '''create_superuser():
                • Sets defaults:
                - is_staff=True
                - is_superuser=True''', **method_node_attrs)

        # creates arrows that connect the method nodes
        dot.edge('mgr', 'private')
        dot.edge('private', 'create')
        dot.edge('private', 'super')

    # -------- Displays the CustomUser Model Methods -----------
    with dot.subgraph(name='cluster_methods') as c:
        c.attr(style='filled,rounded',
               label='Instance Methods',
               fillcolor='#e8f5e9',
               fontsize='16')
        
        # returns custom properties 
        c.node('methods', 'Core Methods (properties)\n─────────────────', **method_node_attrs)
        c.node('name1', '''get_full_name():
        Returns "First Last"''', **method_node_attrs)
        c.node('name2', '''short_name():
        Returns email prefix''', **method_node_attrs)
        c.node('name3', '''user_name:
        Returns either:
        • get_full_name() if exists
        • short_name() as fallback''', **method_node_attrs)
        c.node('img', '''profile_image:
        Returns either:
        • Custom image URL
        • Default image''', **method_node_attrs)
        c.node('time', '''time_since_joined:
        Human-readable
        timedelta''', **method_node_attrs)

        # Corrected edges including name3
        dot.edge('methods', 'name1')
        dot.edge('methods', 'name2')
        dot.edge('methods', 'name3')  # Now properly connected
        dot.edge('methods', 'img')
        dot.edge('methods', 'time')

    # ------- Shows types of validations that occur for fields
    with dot.subgraph(name='cluster_valid') as c:
        c.attr(style='filled,rounded',
               label='Validation Rules',
               fillcolor='#ffebee',
               fontsize='11')
        
        c.node('valid', 'Field Validators\n─────────────────', **method_node_attrs)
        c.node('regex', '''RegexValidator:
• Names: [a-zA-Z-]
• Bio: [a-zA-Z0-9 .,!?-]''', **method_node_attrs)
        c.node('len', '''MaxLengthValidator:
• Names: 75 chars
• Bio: 500 chars
• Job: 50 chars''', **method_node_attrs)
        c.node('file', '''FileExtensionValidator:
• Only JPG/JPEG
allowed''', **method_node_attrs)

        dot.edge('valid', 'regex')
        dot.edge('valid', 'len')
        dot.edge('valid', 'file')

    # ------ how the users a displayed on the admin panel
    dot.node('meta', '''Meta Options (admin panel)
─────────────────
• verbose_name: "CompanyUser"
• verbose_name_plural: "CompanyUsers"''',
             **method_node_attrs, fillcolor='#f5f5f5')

    # try / except block to catch any errors in the generation of the image
    try:
        png_data = dot.pipe(engine='dot', format='png')
        return HttpResponse(png_data, content_type='image/png')
    except Exception as e:
        return HttpResponse(f"Diagram Error: {str(e)}", status=500)