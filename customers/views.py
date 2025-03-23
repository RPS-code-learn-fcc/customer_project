# Django utilities for rendering templates and handling redirects
from django.shortcuts import render, redirect, get_object_or_404

# Django ORM and query utilities
from django.db.models import Q, Case, When, Value, IntegerField, BooleanField

# Django utilities for handling time and timezone-aware datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware

# Django HTTP utilities for responses and pagination
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Django authentication utilities
from django.contrib.auth.decorators import login_required

# Django text utility for generating slugs
from django.utils.text import slugify  

# Import all forms and models from the current app
from .forms import *  
from .models import *  

# Import all models from the app_users app
from app_users.models import *

# Import for creating diagrams (system architecture and ORM views)
from graphviz import Digraph

# Regular expressions module
import re

# Import for generating PDF labels
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas  


# --------------------------- PROJECT LAYOUT VIEWS USING DIGRAPHS / GRAPHVIZ ----------------------------
@login_required    
def architecture_diagram_view(request):
    """View that creates an architecture diagram for the customer_project appliation using the Graphviz library"""
    # creating a new directed graph using Graphviz Python library
    dot = Digraph(format='png') # dot: graph description language
    dot.attr(rankdir='LR') # going left to right
    dot.attr('node', fontname='Arial') # set font and size

    # Main Components/Nodes of the diagram
    dot.node('Frontend', 'Frontend\n(Tailwind CSS, Alpine.js, HTMX)', shape='box', style='filled', fillcolor='lightblue')
    dot.node('Backend', 'Backend\n(Django)', shape='ellipse', style='filled', fillcolor='lightgreen')
    dot.node('Database', 'Database\n(SQLite)', shape='cylinder', style='filled', fillcolor='lightgray')
    dot.node('REST API', 'REST API\n(Django REST Framework)', shape='diamond', style='filled', fillcolor='lightyellow')

    # Connections between nodes
    dot.edge('Frontend', 'Backend', label='Request | Response', dir='both')
    dot.edge('Backend', 'Database', label='Query | Response', dir='both')
    dot.edge('Frontend', 'REST API', label='API Request | Response', dir='both')
    dot.edge('REST API', 'Backend', label='API Request | Response', dir='both')

    # Render the diagram
    png_data = dot.pipe(format='png')
    return HttpResponse(png_data, content_type='image/png')

@login_required    
def orm_diagram_view(request):
    """View that creates an ORM diagram for the appliation using the Graphviz library"""
    # creating a new directed graph using Graphviz Python library
    dot = Digraph(format='png') # dot: graph description language
    dot.attr(rankdir='TB')  # Top-to-bottom layout
    dot.attr('node', fontname='Arial') # set font, etc.

    # Title Node with syling
    dot.node('Title', 'Django ORM Flow', shape='plaintext', fontsize='20', fontcolor='black')

    # Model Node with styling
    dot.node('Model', 'Customer Model (Class)', shape='box', style='rounded,filled', fillcolor='lightblue')

    # Create Instance Customer Node
    dot.node('CreateInstance', 'Create Instance\nCustomer(first_name="John", last_name="Smith", customer_type="person)', shape='box', style='rounded,filled', fillcolor='lightblue')

    # ORM Node
    dot.node('ORM', 'Django ORM', shape='record', style='rounded,filled', fillcolor='lightgreen')

    # Database Table Node using plain text showing customer table / entry                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
    dot.node('DBTable', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
        <TR><TD COLSPAN="3"><B>Customer Table</B></TD></TR>
        <TR><TD><B>ID</B></TD><TD><B>First Name</B></TD><TD><B>Last Name</B></TD></TR>
        <TR><TD>1</TD><TD>John</TD><TD>Smith</TD></TR>
        </TABLE>
    >''', shape='plain')

    # SQLite Database Node
    dot.node('SQLiteDB', 'SQLite Database', shape='box', style='rounded,filled', fillcolor='lightgray')

    # Migration Node
    dot.node('Migration', 'Run Migrations', shape='box', style='rounded,filled', fillcolor='lightblue')

    # Primary Key Returned Node
    dot.node('DBQuery', 'instance.first_name= John', shape='box', style='rounded,filled', fillcolor='lightblue')

    # Create Connections between nodes and label them
    dot.edge('Title', 'Model', label='')
    dot.edge('Model', 'CreateInstance', label='Instantiate')
    dot.edge('CreateInstance', 'ORM', label='Translate to SQL')
    dot.edge('ORM', 'DBTable', label='Create Row in Table')
    dot.edge('DBTable', 'SQLiteDB', label='Store in Database: \ncustomers_customer')
    dot.edge('Model', 'Migration', label='Apply Changes')
    dot.edge('Migration', 'SQLiteDB', label='Update Database')
    dot.edge('SQLiteDB', 'DBQuery', label='Return instance data via \nDB Queries & Responses')

    # Render the diagram using an HTTP response
    png_data = dot.pipe(format='png')
    return HttpResponse(png_data, content_type='image/png')

@login_required
def er_diagram_view(request):
    """Renders a view of the ER diagram constructed using Graphviz, pydot and django-extension"""
    return render(request, 'customers/er_diagram.html')

# --------------------------- LANDING PAGE FOR ALL USERS - ONLY VIEW THAT DOESN'T REQUIRE A USER TO BE LOGGED IN ---------------------------
def landing_page(request):
    """
        Render the landing page of the application.
        This view function is responsible for rendering the base.html template, which serves as the landing page of the application.
        Only view that does not require the user to login - prompts the user to login
    """
    return render(request, 'base.html')

# --------------------------- HOME FEED & FILTERING OF HOME FEED: interestes, dates or users ----------------------------
def parse_date(date_string):
    """ 
        Helper function that parses a date string into a timezone-aware datetime object. Supports multiple date formats, else it returns a ValueError
        Args:
            date_string (str): The date string to be parsed.

        Returns:
            datetime: A timezone-aware datetime object representing the parsed date.

        Raises:
            ValueError: If the date format is not recognized.
    """
    # Define the supported date formats
    formats = ['%Y-%m-%d', '%b. %d, %Y, midnight']  # Add more formats as needed

    # Iterate through each format and attempt to parse the date string
    for fmt in formats:
        try:
            # Attempt to parse the date string using the current format
            parsed_date = datetime.strptime(date_string, fmt)
            # Make the parsed date timezone-aware
            return make_aware(parsed_date)
        except ValueError:
            # If parsing fails, continue to the next format
            continue

    # If parsing fails for all formats, raise a ValueError exception
    raise ValueError(f"Date format not recognized: {date_string}.")

@login_required
def home_view(request, interests=None):
    """
        View for displaying the home page displaying paginated summarized customer profiles.

        home_view:
        - Retrieves & displays a paginated list of customers & displays as a summarized customer profile.
        - Filters customers bassed on: (first name or last name or both).
        - Customer info is ordered by the data of creation (descending)
        - Active customers appear @ the start of the customer list.
        - Users & Interests are provided - this info goes to the aside
        - HTMX requests are allowed & this filters the data: dates, by user crated, etc.
        
        Params:
        - request: HTTP request object
        - interests (opt): A filter parameter for customer interests.

        Returns:
        - Renders  `customers/home.html` template for GET requests.
        - Returns a partial `customers/partials/customers_list.html` template for HTMX requests 
    """
    # Retrieve query parameters from search input
    search_customer = request.GET.get('search_customer')

    # retrieve all users & interests to pass to sidebar
    users = CustomUser.objects.all()
    all_interests = CustomerInterest.objects.all()    

    # Handle search queries (customer names)
    customer_query = Q()
    # if there is a search query - split into search terms
    if search_customer:
        search_terms = search_customer.split()
        for term in search_terms:
            customer_query &= Q(first_name__icontains=term) | Q(last_name__icontains=term)

    # filter customers based on query
    # annotates the customers to put the inactive customers last (they still show up, but are given less priority
    # # creates new field is_active_order
    customers = Customer.objects.filter(customer_query).annotate(
        is_active_order=Case(
            When(is_inactive=True, then=Value(1)),  # Active customers get priority (0)
            When(is_inactive=False, then=Value(0)),  # Inactive customers get lower priority (1)
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('is_active_order', '-created_at')

    # Paginate customer results: shows 10 customers at a time, before pagination
    paginator = Paginator(customers, 10)
    page = request.GET.get('page', 1)
    
    try:
        # tries to paginate the users
        customers = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        # an empty page is returned if there are no more customer entries
        return HttpResponse('<div style="text-align: center; font-weight: bold; margin-top: 20px;">No more customers with matching criteria found.</div>')
    email_prefix = request.user.short_name()
    
    # Prepare context
    context = {
        'customers': customers,
        'page': page,
        'search_customer': search_customer,
        'users': users,
        'interests' : all_interests,
        'user': request.user,
        'email_prefix': email_prefix
    }

    # if there is an htmx request (customer search)
    if request.htmx:
        return render(request, 'customers/partials/customers_list.html', context)

    # Render the full page for standard GET requests
    return render(request, 'customers/home.html', context)

@login_required 
def filter_customers_by_interests(request):
    """
        filters customers based on selected interests (by the user) & displays a partial template w/ the filter list
        uses Q objects to filter the customers
    """

    # gets interests 
    selected_interests = request.GET.getlist('selected_interests', [])

    # get all customers in bdb
    customers = Customer.objects.all()

    # Creatr a Q object query to filter customer interests
    if selected_interests:
        query = Q()  
        for interest_slug in selected_interests:
            query |= Q(interests__slug=interest_slug) 

        # filter customers 
        customers = customers.filter(query).distinct()

    context = {'customers': customers}

    # Render filtered customers
    return render(request, 'customers/partials/customers_list.html', context)

@login_required    
def filter_customers_by_date(request):
    """
        filters customers based on date created - uses the helper function: parse date
        filters customers based on start date, end date or both ( as determined by user input)
        uses Q objects to filter the customers
    """

    # get dates
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # empty query
    query = Q()
    
    # both dates are provided
    if start_date and end_date:
        try:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date) + timedelta(days=1) - timedelta(microseconds=1)
            # Create a query to filter customers by date range
            query = Q(created_at__gte=start_date) & Q(created_at__lte=end_date)
        except Exception as e:
            pass
    
    # only start date
    elif start_date:
        try:
            start_date = parse_date(start_date)
            # Create a query to filter customers by start date
            query = Q(created_at__gte=start_date)
        except Exception as e:
            pass
    
    # only end date
    elif end_date:
        try:
            end_date = parse_date(end_date) + timedelta(days=1) - timedelta(microseconds=1)
            # Create a query to filter customers by end date
            query = Q(created_at__lte=end_date)
        except Exception as e:
            pass
    
    # if no dates - empty q()
    else:
        query = Q()
    
    # Filter customers based on date provided & query made
    try:
        customers = Customer.objects.filter(query).distinct()
    except Exception as e:
        # Handle any errors 
        customers = []
    
    context = {'customers': customers}
    
    return render(request, 'customers/partials/customers_list.html', context)

@login_required    
def filter_customers_by_users(request):
    """
        Filters customers based on the selected creator(s) of customer records provided via GET request.
    """

    # gets the ID's of teh selected users
    selected_user_ids = request.GET.getlist('selected_users', [])

    # gets all customers
    customers = Customer.objects.all()

    # filter the customers based on selected creator ids
    if selected_user_ids:
        customers = customers.filter(creator__id__in=selected_user_ids)

    context = {'customers': customers}

    return render(request, 'customers/partials/customers_list.html', context)

#------------------------------ SEARCH VIEWS: customers, addresses, phone numbers, emails, notes & documents ---------------------
@login_required
def search_addresses(request):
    """
        Searches for customer addresses (mailing addresses when creating mailing lists or addresses from the home page) 
    """
    # gets search query parameters 
    search_address = request.GET.get('search_address', '').strip()
    search_mailing_address = request.GET.get('search_mailing_address', '').strip()

    # is this a search of mailing address
    mailing_flag = 'search_mailing_address' in request.GET

    page = request.GET.get('page', 1)

    # Normalize input: Remove commas & extra spaces
    search_input = search_address if search_address else search_mailing_address
    normalized_search_input = re.sub(r'[,\s]+', ' ', search_input)
    search_terms = normalized_search_input.split()

    query = Q()

    # Construct search query: Match terms across street, city, state, and zip code fields
    for term in search_terms:
        query &= (
            Q(addresses__street__icontains=term) |
            Q(addresses__city__icontains=term) |
            Q(addresses__state__icontains=term) |
            Q(addresses__zip_code__icontains=term)
        )

    # Filter customers based on the constructed query
    customers = Customer.objects.filter(query).distinct()

    # If no search terms are provided,no customers will be returned
    if not search_terms:
        customers = Customer.objects.none()

    # Order results: Prioritize active customers and sort by creation date (descending)
    customers = customers.order_by('is_inactive', '-created_at')

    # Paginate results (10 customers per page)
    paginator = Paginator(customers, 10)
    customers_page = paginator.get_page(page)

    return render(request, 'customers/partials/addresses_list.html', {
        'customers': customers_page,
        'page': customers_page.number,
        'mailing_flag': mailing_flag
    })
    
def normalize_phone_number(phone):
    """       
        Normalizes a phone number by removing any non-numeric characters and formatting it 
        into the standard '###-###-####' format if it contains exactly 10 digits.
    """
    #remove any non-numbers:
    phone = re.sub(r'\D', '', phone)
    
    # normalize phone number format to the same as how it is saved in the DB: '###-###-####'
    if len(phone) == 10:
        return f'{phone[:3]}-{phone[3:6]}-{phone[6:]}'
    # return the formatted phone number
    return phone

@login_required    
def search_phones(request):
    """
     Gets the search query from the request ( what user searches from the home page),
     normalizes the phone number, and filters customers to show customers with matching phone numbers
    """
    # get the phone query
    search_phone = request.GET.get('search_phone', '')
    page = request.GET.get('page', 1)

    if search_phone:
        # Normalize the input phone number
        normalized_number = normalize_phone_number(search_phone)
        
        # create search query w/ norm. phone #
        query = Q(phones__phone_number__icontains=normalized_number)

        # filter customers based on query
        customers = Customer.objects.filter(query).distinct()
    else:
        # no customers returned if nothing is searched
        customers = Customer.objects.none()

    # Paginate the results (10 customers per page)
    paginator = Paginator(customers, 10)
    customers_page = paginator.get_page(page)

    return render(request, 'customers/partials/phones_list.html', {'customers': customers_page, 'page': customers_page.number})

@login_required
def search_emails(request):
    """
       Gets the search query from the request ( what user searches from the home page),
        and filters customers to show customers with matching emails
    """
    # Retrieve search query 
    search_email = request.GET.get('search_email')
    page = request.GET.get('page', 1)

    if search_email:
        # create a search query 
        query = Q(emails__email_address__icontains=search_email)

        # gets customers matching the query, ordered by inactivity status and creation date
        customers = Customer.objects.filter(query).distinct().order_by('is_inactive', '-created_at')
    else:
        # if nothing is searched, no customers are returned
        customers = Customer.objects.none()

    # Paginate the results (10 customers per page)
    paginator = Paginator(customers, 10)
    customers_page = paginator.get_page(page)
    
    return render(request, 'customers/partials/emails_list.html', {'customers': customers_page, 'page':customers_page.number})

@login_required
def search_notes(request):
    """
        searches customers based on user search query provided (from home page) and filters the customers based on this query
        filters customer based on the contents of customer notes
    """
    search_note = request.GET.get('search_note', '')  # Get search query from request
    page = request.GET.get('page', 1)  # Get page number from request
    
    if search_note:
        query = Q(note__icontains=search_note)  # Search notes containing the query string
        notes = CustomerNote.objects.filter(query).distinct()
        
        # Annotate notes 
        notes = notes.annotate(
            customer_inactive=Case(
                When(customer__is_inactive=True, then=Value(0)),  # Inactive customers: 0
                default=Value(1),  # Active customers: 1
                output_field=BooleanField()
            )
        ).order_by('-customer_inactive', '-created_at')  # Sort by inactive first, then most recent
    else:
        notes = CustomerNote.objects.none()  # Return empty queryset if no search term provided
    
    # Paginate results (10 notes per page)
    paginator = Paginator(notes, 10)
    customers_page = paginator.get_page(page)
    
    return render(request, 'customers/partials/notes_list.html', {'notes': notes, 'page': customers_page.number})

@login_required
def search_documents(request):
    """
        searches customers based on user search query provided (from home page) and filters the customers based on this query
        filters customer based on the associated customer document names
    """
    search_document = request.GET.get('search_document', '')  # Get search query from request
    page = request.GET.get('page', 1)  # Get page number from request

    if search_document:
        # Build query to search for matching documents
        query = (
            Q(file__icontains=search_document) |  # Search in file names
            Q(file_detail__icontains=search_document)  # Search in file details
        )
        documents = CustomerDocument.objects.filter(query).distinct()
        
        # Annotate documents with the inactive status of their related customer
        documents = documents.annotate(
            customer_inactive=Case(
                When(customer__is_inactive=True, then=Value(0)),  # Inactive customers → 0
                default=Value(1),  # Active customers → 1
                output_field=BooleanField()
            )
        ).order_by('-customer_inactive', '-created_at')  # Sort by inactive first, then most recent
    else:
        documents = CustomerDocument.objects.none()  # Return empty queryset if no search term is provided
    
    # Paginate results (10 documents per page)
    paginator = Paginator(documents, 10)
    customers_page = paginator.get_page(page)
    
    return render(request, 'customers/partials/documents_list.html', {'documents': documents, 'page': customers_page.number})

@login_required
def search_customers_mailing_list(request):
    """    
        Searches for customers based on user input (first name, last name or both) when creating a mailing list
        and returns a filtered list of customers

    """
    # get the search from user input 
    search_customer = request.GET.get('search_mailing_customer')

    mailing_flag = 'search_mailing_customer' in request.GET  

    # create empty Q object
    customer_query = Q()

    # if something is searched by the user
    if search_customer:
        # Split input into its terms (by spaces)
        search_terms = search_customer.split()
        
        # can search by first, last or both names
        for term in search_terms:
            customer_query &= Q(first_name__icontains=term) | Q(last_name__icontains=term)

        # filter customers
        customers = Customer.objects.filter(customer_query).distinct()

    else: 
        # if nothing is searched, nothing is returned
        customers = Customer.objects.none()

    paginator = Paginator(customers, 5)
    page = request.GET.get('page', 1)

    try:
        customers = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        # If the page number is invalid
        return HttpResponse('')

    # Prepare the context data for rendering the response
    context = {
        'customers': customers,        
        'page': page,                   
        'search_customer': search_customer, 
        'mailing_flag': mailing_flag     
    }
    return render(request, 'customers/partials/list_customers_mailing.html', context)  # Ensure this template exists

# --------------------------- CUSTOMER SIGN-UP PROCESS: Creation of new customer ----------------------------

# define all forms to be used in the multi-step sign-up process - in the order they will be used
FORM_CLASSES = [
    CreateCustomerForm,
    CreateAddressForm,
    CreatePhoneForm,
    CreateEmailForm,
    CreateDocumentForm,
    CreateNoteForm,
]

def process_partial_form(form, customer, request):
    """ Helper Function Determines what instance of the form is present in the signup process for the customer partials view"""
    
    instance = form.save(commit=False)

    if isinstance(form, CreateAddressForm):
        instance.save()
        customer.addresses.add(instance)

    elif isinstance(form, CreatePhoneForm):
        instance.save()
        customer.phones.add(instance)

    elif isinstance(form, CreateEmailForm):
        instance.save()
        customer.emails.add(instance)

    elif isinstance(form, CreateDocumentForm):
        instance.customer = customer
        instance.author = request.user  # This should ONLY happen in CreateDocumentForm
        instance.save()

    elif isinstance(form, CreateNoteForm):
        instance.customer = customer
        instance.author = request.user  # This should ONLY happen in CreateNoteForm
        instance.save()

@login_required    
def create_customer_view(request):
    """
        Handles the multi-step customer creation/ sign-up process.
        
        - Step 0: Create a customer and in the session, store this new customer i.d.
        - Steps 1+: Add an address, phone #, etc.that is associated with the newly created customer
        - If all steps are completed, the user is redirected to a successful signup page.
    """
    # Initialize or reset signup step in the session
    step = request.session.get('signup_step', 0)

    # If step exceeds the available forms, redirect to home page
    if step >= len(FORM_CLASSES):
        return redirect("home")

    # Get the appropriate form for the current step
    FormClass = FORM_CLASSES[step]
    form = FormClass(request.POST or None, request.FILES or None)

    # Handle POST requests
    if request.method == "POST" and form.is_valid():
        if step == 0:  # First step: Create the customer
            customer = form.save(commit=False)
            customer.creator = request.user
            customer.save()
            form.save_m2m()
            request.session['customer_id'] = customer.id
        else:  # Subsequent steps: Update related information
            customer_id = request.session.get('customer_id')
            if not customer_id:
                return redirect("sign_up_error")
            customer = get_object_or_404(Customer, id=customer_id)
            process_partial_form(form, customer, request)

        # Increment the step and save it to the session
        step += 1
        request.session['signup_step'] = step

        if step < len(FORM_CLASSES):
            return redirect("create_customer_view")

        return redirect("create_customer_success")

    # Render the create customer page
    template = "customers/create_new_customer.html"
    context = {"form": form, "step": step + 1, "total_steps": len(FORM_CLASSES)}
    return render(request, template, context)

@login_required
def create_customer_partial_view(request):
    """
        Handles multi-step customer creation using HTMX.

        The sign up of a customer, each step is stored in the session (session management).
        - Step 0: a new customer is created & a creator is assigned ( the user that is authenticated for the current session)
        - Steps 1-6: Add an address, phone #, etc.that is associated with the newly created customer
        - Dynamic form handling validates the data
        - Successful signup - redirect to success page
        - Errors - redirected to error page
    """
    step = request.session.get("signup_step", 0)

    if step >= len(FORM_CLASSES):
        return redirect("home")

    FormClass = FORM_CLASSES[step]
    form = FormClass(request.POST or None, request.FILES or None)

    # Extract non-field errors for display
    form_errors = form.non_field_errors()

    if request.method == "POST":
        if form.is_valid():
            customer_id = request.session.get("customer_id")

            if step == 0:
                # Create a new customer
                customer = form.save(commit=False)
                customer.creator = request.user
                customer.save()
                form.save_m2m()
                request.session["customer_id"] = customer.id

            else:
                # Retrieve existing customer
                if not customer_id:
                    return redirect("sign_up_error")

                customer = get_object_or_404(Customer, id=customer_id)
                process_partial_form(form, customer, request)

            # Move to the next step
            step += 1
            request.session["signup_step"] = step

            # If more steps remain, render the next form
            if step < len(FORM_CLASSES):
                next_form = FORM_CLASSES[step]()
                return render(request, "customers/partials/signup_form.html", {
                    "form": next_form,
                    "step": step + 1,
                    "total_steps": len(FORM_CLASSES),
                    "form_errors": None
                })

            return redirect("create_customer_success")  # Final step completed

    # Render the partial form for HTMX requests, including validation errors if any
    return render(request, "customers/partials/signup_form.html", {
        "form": form,
        "step": step + 1,
        "total_steps": len(FORM_CLASSES),
        "form_errors": form_errors,
    })

@login_required    
def create_customer_success(request):
    """    
        Handles the final step of the customer signup process, after 6 steps.

        - Retrieves the newly created customer from the session.
        - Clears session variables (`signup_step` and `customer_id`) to allow new customer signups.
        - Renders a success page displaying the created customer’s details.
    """
    
    # Clear session variables after successful customer signup
    cust_id = request.session['customer_id']
    
    # retrieve a customer if the customer id exists
    customer = get_object_or_404(Customer, id=cust_id)
    
    # remove the step and customer id -> a new customer can now be created
    request.session.pop('signup_step', None)
    request.session.pop('customer_id', None)
    
    template =  "customers/signup_success.html"
    context = {'customer': customer}

    return render(request,template, context)

@login_required
def sign_up_error(request):
    """
        View that handles errors in the signup process
    """
    return render(
        request,
        "customers/signup_error.html",
        {"message": "An error occurred when attempting to add the customer. Please return home and try again."}
    )

@login_required
def cancel_signup(request):
    """
    Cancels an ongoing , multi-step new customer signup process.

    - If a customer record exists in the session, this customer and assoicated data (documents, etc.) are delted
    - Session variables (`signup_step` and `customer_id`) are cleared, allowing new customer signups

    Returns:
        - A redirect to the cancellation confirmation page if successful.
        - A redirect to the home page in case of an error.
    """
    # Retrieve the customer ID from the session
    customer_id = request.session.get('customer_id')

    if customer_id:
        try:
            # Retrieve and delete the customer record
            customer = get_object_or_404(Customer, id=customer_id)
            customer.delete()  # Deletes related objects if cascade deletion is set
        except Exception as e:
            return redirect('sign_up_error')  # Redirect home in case of error

    # Clear session data to allow a fresh signup process
    request.session.pop('signup_step', None)
    request.session.pop('customer_id', None)

    # Redirect to a cancellation confirmation page
    return redirect('cancel_confirmation')

@login_required
def cancel_confirmation(request):
    """
        View that is shown to the user when the multi-step customer signup process is cancelled
    """
    return render(request, 'customers/signup_cancel_confirmation.html')

@login_required
def create_customer_back_step(request):
    """
        Handles navigating back one step in the multi-step customer signup process.

        This view allows users to go back to the previous step in the form flow.
        - Updates the session variable (`signup_step`) to the previous step.
        - Retrieves the corresponding form class for the updated step.
        - Prefills the form with previously submitted data (if applicable).
        - If the form corresponds to a related model (e.g., addresses, phones, emails), 
        it retrieves the latest instance.
        - Returns the updated form as an HTMX partial or redirects to the main signup view.

        Returns:
            - A rendered form for HTMX requests.
            - A redirect to the main signup view if HTMX is not used.
    """

    # Retrieve the current step from session
    step = request.session.get('signup_step', 0)

    # Ensure the step does not go below zero
    if step > 0:
        step -= 1
    request.session['signup_step'] = step  # Save the updated step in session

    # Retrieve the form class for the current step
    FormClass = FORM_CLASSES[step]

    # Retrieve previously submitted data
    if step == 0:
        # First step: Attempt to prefill customer data if available
        customer_id = request.session.get('customer_id')
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            form = FormClass(instance=customer)
        else:
            form = FormClass()  # Provide a blank form if no customer exists yet
    else:
        # Retrieve existing customer data for later steps
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect("sign_up_error")  # Redirect if no customer data is found

        customer = get_object_or_404(Customer, id=customer_id)

        # Determine the instance for the specific form type (addresses, phones, emails, etc.)
        if FormClass == CreateAddressForm:
            instance = customer.addresses.last()
        elif FormClass == CreatePhoneForm:
            instance = customer.phones.last()
        elif FormClass == CreateEmailForm:
            instance = customer.emails.last()
        elif FormClass == CreateDocumentForm:
            try:
                instance = customer.documents.get()  # Retrieve single document if it exists
            except CustomerDocument.DoesNotExist:
                instance = None
        elif FormClass == CreateNoteForm:
            instance = customer.notes.last()
        else:
            instance = None  # Default case for unknown form types

        form = FormClass(instance=instance)  # Populate form with the retrieved instance

    # If the request is an HTMX request, render the form as a partial
    if request.htmx:
        return render(
            request,
            "customers/partials/signup_form.html",
            {
                "form": form,
                "step": step + 1,  # Display step index starting from 1
                "total_steps": len(FORM_CLASSES),
            },
        )

    # If not an HTMX request, redirect to the full signup view
    return redirect("create_customer_view")


@login_required
def create_customer_skip_step(request):
    """
    Skips a step in the multi-step customer sign-up process.

    Increases the step number stored in the session (session management)

    - HTMX request: returns the next step's form as a partial 
    """
    # gets current session step
    step = request.session.get('signup_step', 0)
    
    # Increments step 
    step += 1
    request.session['signup_step'] = step

    # redirects to success page if step > 6
    if step >= len(FORM_CLASSES):
        return redirect("create_customer_success")

    # Get the next form class based on the current step
    FormClass = FORM_CLASSES[step]
    form = FormClass()

    if request.htmx:
        return render(
            request,
            "customers/partials/signup_form.html",
            {
                "form": form,
                "step": step + 1,  
                "total_steps": len(FORM_CLASSES),
            },
        )

    return redirect("create_customer_view")

@login_required    
def view_newest_customer_profile(request):
    """
        Gets the most recently created customer profile that was created by the current user

    """
    # Get the newest customer created by the current user
    newest_customer = Customer.objects.filter(creator=request.user).order_by('-created_at').first()

    if not newest_customer:
        return render(request, '404.html') # handle no recent customers or cannot find this page

    return view_full_customer_profile(request, newest_customer.id)

# --------------------------- VIEW PROFILE INFORMATION ---------------------
@login_required    
def view_full_customer_profile(request, customer_id):
    """View to view full customer information - uses customer_id to retrieve the correct customer info"""
    # Retrieve the customer for the given ID
    customer = get_object_or_404(Customer, id=customer_id)

    # Retrieve associated notes and documents
    customer_notes = customer.notes.all()
    customer_documents = customer.documents.all()
        
    # Template and context
    template = 'customers/view_customer_profile.html'
    context = {
        'customer': customer,
        'customer_notes': customer_notes,
        'customer_documents': customer_documents,
    }
    return render(request, template, context)

@login_required
def toggle_inactive_status(request, customer_id):
    """Toggles a customer profile account to inactive using the customer_id"""
    # get the appropriate customer instance
    customer = get_object_or_404(Customer, id=customer_id)

    # if it is a post request
    if request.method == "POST":
        # Toggle the is_inactive field
        customer.is_inactive = not customer.is_inactive
        customer.save()

        # Prepare the updated status and button text
        status_text = (
            '<span class="text-danger">Inactive</span>'
            if customer.is_inactive
            else '<span class="text-success">Active</span>'
        )
        
        button_text = "Mark Active" if customer.is_inactive else "Mark Inactive"

        # Return a JSON response with the updated values
        return JsonResponse({
            "status_text": status_text,
            "button_text": button_text,
            "is_inactive": customer.is_inactive,
        })

    # Return an error for non-POST requests
    return JsonResponse({"error": "Invalid request method"}, status=400)

# ----------------------------- ADD NEW CUSTOMER INFO: address, email, phone, note, document or interest ---------------------------
@login_required
def add_address(request, customer_id):
    """adds an address to a customer instance, using the customer_id"""
    
    # gets the appropirate customer instance
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    
    # if it is a POST rquest
    if request.method == 'POST':
        # send data to form
        form = CreateAddressForm(request.POST)
        # if the form is valid
        if form.is_valid():
            address = form.save() # save teh address
            customer.addresses.add(address) # add the address to the customer address
            # redirect to view the updated customer profile
            return redirect('view_customer_profile', customer_id=customer_id)
    else:
        form = CreateAddressForm()
    
    template ='customers/add_address.html'
    context = {'customer': customer, 'form': form}
    return render(request, template, context)

@login_required
def add_email(request, customer_id):
    """View to add an email to a customer instance, providing the customer_id"""
    
    # get appropriate customer instance
    customer = get_object_or_404(Customer, id=customer_id)
    # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    
    # if it is a post rquest
    if request.method == 'POST':
        form = CreateEmailForm(request.POST)
        if form.is_valid(): # check that the form is valid
            email = form.save() # save teh email
            customer.emails.add(email) # add the email to the customer instance
            # redirect to the full customer profile view
            return redirect('view_customer_profile', customer_id=customer_id) 
    else:
        form = CreateEmailForm()
    template ='customers/add_email.html'
    context = {'customer': customer, 'form': form}
    return render(request, template, context)

@login_required
def add_phone(request, customer_id):
    """View to add a phone number to a customer instance, providing the customer_id"""
    # get appropriate customer instance
    customer = get_object_or_404(Customer, id=customer_id)
    # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    # if it is a post request
    if request.method == 'POST':
        form = CreatePhoneForm(request.POST)
        if form.is_valid(): # if the form is valid
            phone = form.save() # save the phone number
            customer.phones.add(phone) # add the phone number to the customer instance
            # redirect to the full customer profile view
            return redirect('view_customer_profile', customer_id=customer_id) 
    else:
        form = CreatePhoneForm()
    template ='customers/add_phone.html'
    context = {'customer': customer, 'form': form}
    return render(request, template, context)

@login_required
def add_note(request, customer_id):
    """View to add a note to a customer instance, providing the customer_id"""
    # get appropriate customer instance
    customer = get_object_or_404(Customer, id=customer_id)

    # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    # if it is a post request
    if request.method == 'POST':
        form = CreateNoteForm(request.POST)
        if form.is_valid(): # if the form is valid
            note = form.save(commit=False)
            note.author = request.user # save the author of the note as the request.cuser
            note.customer = customer #  sets the customer field of note to reference customer instance
            note.save()
            
            return redirect('view_customer_profile', customer_id=customer_id)  
    else:
        form = CreateNoteForm()
    template ='customers/add_note.html'
    context = {'customer': customer, 'form': form}
    return render(request, template, context)

@login_required
def add_document(request, customer_id):
    """View to add a document to a customer instance, providing the customer_id"""
    # get appropriate customer instance
    # Redirect or show different view if customer is inactive
    customer = get_object_or_404(Customer, id=customer_id)
    # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    if request.method == 'POST':
        form = CreateDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.author = request.user # save the author of the note as the request.user
            document.customer = customer #  sets the customer field of document to reference customer instance
            document.save()
            # redirect to ful customer profile view            
            return redirect('view_customer_profile', customer_id=customer_id) 
    else:
        form = CreateDocumentForm()
    template ='customers/add_document.html'
    context = {'customer': customer, 'form': form}
    return render(request, template, context)

@login_required  
def add_interest(request):  
    """Add a new interest view"""
    if request.method == 'POST':  
        form = CreateCustomerInterest(request.POST, request.FILES)  # Add request.FILES here
        if form.is_valid():  
            interest = form.save(commit=False)  
            interest.slug = slugify(interest.name)  # Create a URL-friendly slug
            interest.save()  
            return redirect('home')  
    else:  
        form = CreateCustomerInterest()  
    return render(request, 'customers/add_interest.html', {'form': form})

@login_required
def add_contact_method(request):
    """Add a new customer contact method."""
    if request.method == 'POST':
        form = CreateCustomerContactMethod(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.save() 
            return redirect('home')  # Redirect to the home page after saving
    else:
        form = CreateCustomerContactMethod()
    return render(request, 'customers/add_contact_method.html', {'form': form})

# --------------------------- MAILING LIST CREATION ----------------------------
@login_required
def create_customer_mailing_list(request):
    """View to create a customer mailing list"""
    
    if request.method == 'POST':
        form = CreateCustomerMailingListForm(request.POST)

        # Get the selected address IDs from the request
        selected_address_ids = request.POST.get("selected_addresses", "").split(",")
        selected_address_ids = [int(id) for id in selected_address_ids if id.strip().isdigit()]

        print("Selected Address IDs:", selected_address_ids)

        if form.is_valid():
            # Save the mailing list instance first
            mailing_list = form.save(commit=False)  # Create the object but don't save M2M fields yet
            mailing_list.save()  # Now it has an ID!

            # Save ManyToMany relationships (Interests)
            form.save_m2m()  

            # Fetch the selected Address objects
            selected_addresses = Address.objects.filter(id__in=selected_address_ids)
            print("Selected Addresses:", selected_addresses)

            # Get Customers Associated with the Selected Addresses
            customers = Customer.objects.filter(addresses__in=selected_addresses).distinct()
            print("Customers Added to Mailing List:", customers)

            # Add Customers to the Mailing List
            mailing_list.customers.add(*customers)  
            mailing_list.addresses.add(*selected_addresses)  


            return redirect('list-mailing-lists')
    else:
        form = CreateCustomerMailingListForm()

    return render(request, 'customers/create_mailing_list.html', {'form': form})

@login_required
def interest_customer_count(request):
    """ HTMX view to count the number of customers based on selected interests to display on the create mailing list page """
    
    # Fix extraction: split by commas if single string, otherwise get a list of ids
    selected_interests_raw = request.GET.get('selected_interests', '')  # Get as a string
    selected_interest_ids = selected_interests_raw.split(",") if selected_interests_raw else []

    # if no customers are selected
    if not selected_interest_ids:
        return JsonResponse({'total_customers': 0})

    # retrieve any customers who have any of the selected interests and
    customers = Customer.objects.filter(
        interests__id__in=selected_interest_ids,  # Match selected interests
        addresses__mailing_address=True  # Ensure at least one address has mailing_address=True
    ).distinct()
    return JsonResponse({'total_customers': customers.count()})

@login_required
def view_mailing_list_details(request, pk):
    """View that shows the mailing list details of an individual mailing list by primary key supplied"""
    # Retrieve the mailing list or return a 404 if not found
    mailing_list = get_object_or_404(CustomerMailingList, pk=pk)

    return render(request, "customers/mailing_list_details.html", {"mailing_list": mailing_list})

@login_required
def list_mailing_lists(request):
    """view that retreives all mailing lists from the db"""
    try:
        mailing_lists = CustomerMailingList.objects.all()
    except Exception as e:
        return HttpResponseServerError("An error occurred while fetching mailing lists.")

    context = {
        "mailing_lists": mailing_lists
    }
    return render(request, "customers/list_mailing_lists.html", context)

@login_required
def add_selected_address_list(request):
    """Handles HTMX request to add a selected address to a mailing list and returns an HTML snippet."""
    # if it is a post request
    if request.method == "POST":
        # Retrieve form data
        address_id = request.POST.get("address_id")
        customer_id = request.POST.get("customer_id")

        # Ensure required fields are present to add an addrss or customer id
        if not address_id or not customer_id:
            return HttpResponse("Missing address or customer parameters", status=400)

        # Retrieve the Address and Customer objects
        address = get_object_or_404(Address, id=address_id)
        customer = get_object_or_404(Customer, id=customer_id)

        # Render and return the updated address selection UI
        return render(
            request, 
            "customers/partials/selected_address.html", 
            {"address": address, "customer": customer}
        )

    return HttpResponse(status=400)  # Return bad request for non-POST requests

@login_required
def remove_selected_address_list(request):
    """HTMX request that removes an already selected mailing addres from an already created mailing list"""
    if request.method == "POST":
        # gets the address id of the address to remove
        address_id = request.POST.get("address_id")

        # if the id is not sent in the request
        if not address_id:
            return JsonResponse({"error": "Missing address ID"}, status=400)

        # Get the address object to make sure it exists
        address = get_object_or_404(Address, id=address_id)

        # Return an empty response because `hx-swap="delete"` removes it from the UI
        return JsonResponse({}, status=204)  # 204 means "No Content"
    # else return an error
    return JsonResponse({"error": "Invalid request"}, status=400)

# ------------ UPDATES CUSTOMER INFO: customer, address, phone, email, note or document -------------------------------
@login_required
def edit_customer(request, customer_id):
    """View to edit basic customer information: customer name, etc. based on supplied customer id"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Redirect or show different view if customer is inactive (cannot edit it)
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)

    if request.method == 'POST':
        form = CreateCustomerForm(request.POST, instance=customer) # populate the form with data
        if form.is_valid():# if the form is valid, save the instance
            form.save()
            return redirect('view_customer_profile', customer_id=customer_id) # redirect to view the updated customer profile
    else:
        form = CreateCustomerForm(instance=customer)
    template ='customers/edit_customer.html'
    context = {'customer': customer, 'form': form}
    return render(request, template, context)

@login_required
def address_edit_view(request, customer_id, address_pk):
    """View to edit an individual customer address given the customer id and address id"""
    customer = get_object_or_404(Customer, pk=customer_id)
    # Redirect or show different view if customer is inactive (cannot add an address)
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    # get the corresponding customer address
    address = get_object_or_404(customer.addresses, pk=address_pk)
    if request.method == "POST":
        form = CreateAddressForm(request.POST, instance=address) # populates form with address data to edit
        if form.is_valid():
            form.save()  
            return redirect('view_customer_profile', customer.id ) # redirects to updated customer profile
    else:
        form = CreateAddressForm(instance=address)

    context = {
        'customer': customer,
        'address': address,
        'form': form,
    }
    return render(request, 'customers/edit_address.html', context)

@login_required
def phone_edit_view(request, customer_id, phone_pk):
    """View to edit an individual customer phone number given the customer id and phone id"""

    # get customer and phone instances
    customer = get_object_or_404(Customer, pk=customer_id)
    phone = get_object_or_404(customer.phones, pk=phone_pk)
        # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    if request.method == "POST":
        form = CreatePhoneForm(request.POST, instance=phone) # populate the form with phone number data to edit
        if form.is_valid():
            form.save()  # This updates both the description and the file
            return redirect('view_customer_profile', customer.id )

    else:
        form = CreatePhoneForm(instance=phone)

    context = {
        'customer': customer,
        'phone': phone,
        'form': form,
    }
    return render(request, 'customers/edit_phone.html', context)

@login_required
def email_edit_view(request, customer_id, email_pk):
    """View to edit an individual customer email given the customer id and email id"""

    # get the corresponding customer and email instances
    customer = get_object_or_404(Customer, pk=customer_id)
    email = get_object_or_404(customer.emails, pk=email_pk)  
    # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    
    if request.method == "POST":
        form = CreateEmailForm(request.POST, instance=email) # populate the form with the email data to edit
        if form.is_valid():
            form.save()  # Save the updated email instance
            return redirect('view_customer_profile', customer.id)

    else:
        form = CreateEmailForm(instance=email)

    context = {
        'customer': customer,
        'email': email,
        'form': form,
    }
    return render(request, 'customers/edit_email.html', context)

@login_required
def note_edit_view(request, customer_id, note_pk):
    """View to edit an individual customer note given the customer id and note id"""
    # get the corresponding customer and note instances
    customer = get_object_or_404(Customer, pk=customer_id)
    # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
 
    note = get_object_or_404(customer.notes, pk=note_pk)
    if request.method == "POST":
        form = CreateNoteForm(request.POST, instance=note, user=request.user) # populate the form with the note data to edit and user that is editing the note
        if form.is_valid():
            form.save()  # save the updated note instance
            return redirect('view-all-notes', customer.id ) # redirect to view all customer notes

    else:
        form = CreateNoteForm(instance=note, user=request.user)
    # get the associated note history
  
    context = {
        'customer': customer,
        'note': note,
        'form': form,

    }
    return render(request, 'customers/note_edit.html', context)

@login_required    
def document_edit_view(request, customer_id, document_pk):
    """View to edit an individual customer document given the customer id and note id"""

  
    # retrieve the associated customer and document instances
    customer = get_object_or_404(Customer, pk=customer_id)
    document = get_object_or_404(customer.documents, pk=document_pk)
    
    # Redirect or show different view if customer is inactive
    if customer.is_inactive:
        return redirect('view_customer_profile', customer_id=customer_id)
    # if it is a post request
    if request.method == "POST":
        form = CreateDocumentForm(request.POST, request.FILES, instance=document, user=request.user) # populate the form with the document data, file to edit and user that is editing the note
        if form.is_valid():
            form.save()  # This updates both the description and the file
            return redirect('view_customer_profile', customer_id=customer_id) # redirects to updated customer profile
    else:
        form = CreateDocumentForm(instance=document)

    context = {
        'customer': customer,
        'document': document,
        'form': form,
    }
    return render(request, 'customers/edit_document.html', context)

@login_required
def mailing_list_edit_view(request, pk):
    """View to edit a mailing list given the primary key (id)."""
    # Retrieve the correct mailing list
    mailing_list = get_object_or_404(CustomerMailingList, pk=pk)

    # Get preselected interest IDs from customers in the mailing list
    selected_interest_ids = list(
        mailing_list.customers.values_list("interests__id", flat=True).distinct()
    )

    if request.method == "POST":
        form = CreateCustomerMailingListForm(request.POST, instance=mailing_list)  

        if form.is_valid():
            mailing_list = form.save(commit=False)  # Save the form data, but don't commit yet
            mailing_list.save()  # Save the mailing list instance

            # Save ManyToMany relationships (Interests)
            form.save_m2m()

            # Retrieve manually selected addresses from form input
            selected_address_ids = request.POST.get("selected_addresses", "").split(",")
            selected_address_ids = [int(id) for id in selected_address_ids if id.strip().isdigit()]

            #Fetch the selected Address objects**
            selected_addresses = Address.objects.filter(id__in=selected_address_ids)

            # Get customers associated with the selected addresses**
            customers = Customer.objects.filter(addresses__in=selected_addresses).distinct()

            # Update mailing list data (prevents duplicates)**
            mailing_list.addresses.set(selected_addresses)  # Update mailing list addresses
            mailing_list.customers.set(customers)  # Update mailing list customers

            return redirect('view-mailing-list-details', mailing_list.id)  # Redirect to view the updated mailing list

    else:
        form = CreateCustomerMailingListForm(instance=mailing_list)  

    context = {
        'mailing_list': mailing_list,
        'form': form,
        'selected_interest_ids': selected_interest_ids,  # Pass selected interests to template
    }
    return render(request, 'customers/mailing_list_edit.html', context)
# ------------------------------- ADDITIONAL document AND Note views --------------------
@login_required
def note_detail_view(request, customer_id, note_pk):
    """View that shows the full details of a CustomerNote given the customer_id and note_pk"""
    # get associated customer and note instances
    customer = get_object_or_404(Customer, pk=customer_id)
    note = get_object_or_404(customer.notes, pk=note_pk)
    
    # get the associated note history
    history = note.note_history.all().order_by('-edited_at')

    context = {
        'customer': customer,
        'note': note,
        'history':history
    }

    return render(request, 'customers/note_detail.html', context)

@login_required
def all_notes_view(request, customer_id):
    """Lists all notes for a given customer, given a customer id"""
    # Retrieve the customer by ID
    customer = get_object_or_404(Customer, pk=customer_id)
    # Retrieve all notes related to the customer
    notes = customer.notes.all()
    context = {
        'notes': notes,       # Paginated notes for the current page
        'customer': customer,  # The customer object
    }

    # Render the full view for non-HTMX requests
    return render(request, 'customers/notes_view_all.html', context)

@login_required
def document_edit_history(request, customer_id, document_pk):
    """View that shows the edit history for a given document given the customer and document ids"""
    # get the associated customer and document objects
    customer = get_object_or_404(Customer, pk=customer_id)
    document = get_object_or_404(customer.documents, pk=document_pk)
    
    # get the associated document edit history
    history = document.edit_history.all().order_by('-edited_at')
    context = {
        'customer': customer,
        'document': document,
        'history': history,
    }
    return render(request, 'customers/edit_document_history.html', context)

# ------------------------ DELETE -------------------------------------------
@login_required
def document_delete_view(request, customer_id, document_pk):
    """View that deletes a document given a provided customer id and document id"""
    # get the associated customer or 404 page for given customer_id
    customer = get_object_or_404(Customer, id=customer_id)
    
    # get the associated Note instance or 404 page
    document = get_object_or_404(customer.documents, pk=document_pk)
    
    # if it is a post method
    if request.method == "POST":
        document.delete() # delete the document which leads to the cascading delete of document from customer model 
        return redirect('view_customer_profile', customer_id=customer_id)
    
    context = {
        'customer': customer,
        'document': document,
    }
    template = 'customers/document_delete.html'

    return render(request, template, context)

@login_required
def mailing_list_delete_view(request, pk):
    """View that deletes a mailing list given a provided a mailing list id"""

    # get the associated mailing_list or 404 page for given customer_id
    mailing_list = get_object_or_404(CustomerMailingList, id=pk)
    
    # if it is a post method
    if request.method == "POST":
        mailing_list.delete() # delete the mailng list
        return redirect('list-mailing-lists')
    
    context = {
        'mailing_list': mailing_list,
    }
    template = 'customers/delete_mailing_list.html'

    return render(request, template, context)

@login_required
def delete_customer_from_mailing_list(request, mailing_id, customer_id):
    """View that deletes a customer from a mailing list given a provided mailing id and customer id"""

    # get associated mailing list and customer instances
    mailing_list = get_object_or_404(CustomerMailingList, id=mailing_id)
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        if customer in mailing_list.customers.all():
            mailing_list.customers.remove(customer) # remove customers from mailing lists
        #  Detect if the request is from the edit page
        edit_mode = request.POST.get('edit_mode', False)
        
        if request.htmx: # if it is an htmx in edit mode
            if edit_mode: # if in edit mode, render the partial mailing list dettails page
                context = { 'mailing_list' : mailing_list}
                return render(request, 'customers/partials/mailing_list_details.html', context)
            
            else: # renders the success mailing list page if not in edit mode -> Will give user options after successfully deleting / removing a customer from the mailing list
                context = { 'customer_id' : customer_id}
                return render(request, 'customers/partials/delete_customer_success_mailing_list.html', context)

    return render(request, 'customers/delete_customer_mailing_list.html', {
        'mailing_list': mailing_list,
        'customer': customer
    })

@login_required
def address_delete_view(request, customer_id, address_id):
    """View that deletes an address given a provided customer id and address id"""

    # Retrieve the Address object (or return a 404 if not found)
    address = get_object_or_404(Address, pk=address_id)
    
    # Get the ccustomer instance.
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == "POST":
        # Remove the association between the customer and the address.
        customer.addresses.remove(address)
        
        # Optionally, if no customers are associated with this address, delete it.
        if not address.customer_addresses.exists():
            address.delete()
        
        # redirect to the customer profile
        return redirect('view_customer_profile', customer_id)
    
    context = {'address': address, 'customer': customer }
    return render(request, 'customers/delete_address.html', context)

@login_required
def phone_delete_view(request, customer_id, phone_id):
    """View that deletes a phone number given a provided customer id and phone id"""

    # Retrieve the Phone object (or return a 404 if not found)
    phone = get_object_or_404(Phone, pk=phone_id)
    
    # Get the ccustomer instance.
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == "POST":
        # Remove the association between the customer and the phones.
        customer.phones.remove(phone)
        
        # Optionally, if no customers are associated with this phones, delete it.
        if not phone.customer_phones.exists():
            phone.delete()
        
        # redirect to the customer profile
        return redirect('view_customer_profile', customer_id)
    
    context = {'phone': phone, 'customer': customer }
    return render(request, 'customers/delete_phone.html', context)

@login_required
def email_delete_view(request, customer_id, email_id):
    """View that deletes an email given a provided customer id and email id"""

    # Retrieve the email object (or return a 404 if not found)
    email = get_object_or_404(Email, pk=email_id)
    
    # Get the ccustomer instance.
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == "POST":
        # Remove the association between the customer and the email.
        customer.emails.remove(email) # don't delete it, just remove it (as other customers could have the same email)
        
        # Optionally, if no customers are associated with this email, delete it.
        if not email.customer_emails.exists():
            email.delete()
        
        # redirect to the customer profile
        return redirect('view_customer_profile', customer_id)
    
    context = {'address': email, 'customer': customer }
    return render(request, 'customers/delete_email.html', context)

@login_required
def remove_customer_address_from_mailing_list(request, mailing_list_id, customer_id, address_id):
    """
    Removes an address from a mailing list. If the customer has no more addresses in the list, remove them too.
    """
    # Get the mailing list, customer, and address
    mailing_list = get_object_or_404(CustomerMailingList, id=mailing_list_id)
    customer = get_object_or_404(Customer, id=customer_id)
    address = get_object_or_404(Address, id=address_id)

    # Debugging prints
    print(mailing_list.customers.all(), " before")
    print(mailing_list.addresses.all(), " before")
    print(mailing_list, "mailing_list")
    print(customer, "customer")
    print(address, "address")

    # Remove the address from the mailing list
    mailing_list.addresses.remove(address)

    # Check if the customer still has any addresses left in the mailing list
    remaining_addresses = Address.objects.filter(id__in=mailing_list.addresses.all(), customer_addresses=customer)

    if not remaining_addresses.exists():
        mailing_list.customers.remove(customer)  # Remove customer if no addresses remain

    # Status message
    status = "success"
    message = f"The address for {customer.display_name} has been removed from the mailing list."

    # Redirect to the mailing list detail page with status and message in the URL
    redirect_url = reverse('view-mailing-list-details', args=[mailing_list_id])
    redirect_url += f"?status={status}&message={message}"
    return redirect(redirect_url)
# ------------------------ MAILING LIST: Labels & pdf generation -------------------------------------------
@login_required     
def generate_labels_pdf(request, mailing_list_id):
    """View that allows the user to generate pdf labels to create mailing lists - a pdf is downloaded"""
    mailing_list = get_object_or_404(CustomerMailingList, id=mailing_list_id)

    # Generate formatted addresses with the first associated customer's name and address
    formatted_addresses = [
        f"{address.customer_addresses.first().display_name}\n{address.street}\n{address.city}, {address.state} {address.zip_code}"
        for address in mailing_list.addresses.all()
        if address.customer_addresses.exists()  # Ensure the address is linked to at least one customer
    ]

     # get starting position of grid (default to 0 if the user does not click anything on the screen)
    start_position_str = request.POST.get('start_position', '1')  
    try:
        start_position = int(start_position_str) - 1  # Convert to zero-based index
    except ValueError:
        start_position = 0  # Default to 0 if it fails - empty string provided, etc. 

    if start_position < 0:  # make sure the start position is not negative
        start_position = 0

    # PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{mailing_list.name}_mailing_list.pdf"'

    # Set up PDF
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setFont("Helvetica", 10)

    # Avery 5160 Labels (3x10 layout)
    labels_per_row = 3
    labels_per_col = 10
    label_width = 2.625 * inch
    label_height = 1 * inch
    margin_x = 0.5 * inch
    margin_y = 0.5 * inch
    spacing_x = 0.125 * inch
    spacing_y = 0.0 * inch  # Adjust if needed

    # Set the starting X and Y position for labels
    x_start = margin_x
    y_start = letter[1] - margin_y - label_height  # Start from the top-left

    total_labels = labels_per_row * labels_per_col  # 30 labels per page
    
    count = 0  # Tracks actual labels printed
    label_count = start_position  # Includes empty labels for the start position

    # Begin writing text for multi-line support
    text_object = pdf.beginText()
    text_object.setFont("Helvetica", 10)

    for address in formatted_addresses:
        # Calculate row and column based on label_count, not count
        row = label_count // labels_per_row
        col = label_count % labels_per_row

        # Calculate X and Y positions
        x = x_start + col * (label_width + spacing_x)
        y = y_start - row * (label_height + spacing_y)

        # Start a new page if needed
        if label_count > 0 and label_count % total_labels == 0:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            label_count = 0  # Reset label count for new page
            row = label_count // labels_per_row
            col = label_count % labels_per_row
            x = x_start + col * (label_width + spacing_x)
            y = y_start - row * (label_height + spacing_y)

        # Draw the multi-line text
        text_object.setTextOrigin(x + 5, y + label_height - 15)  # Adjust label positioning
        for line in address.split("\n"):  # Split into lines for name + address
            text_object.textLine(line)  # Add each line separately

        pdf.drawText(text_object)  # Render the text
        count += 1
        label_count += 1  # Always increment, to keep track of position

    pdf.save()
    return response

@login_required    
def print_labels_page(request, mailing_list_id):
    """Gets mailing list that will be used to generate pdf labels"""
    mailing_list = get_object_or_404(CustomerMailingList, id=mailing_list_id)
    return render(request, 'customers/print_labels.html', {'mailing_list': mailing_list})