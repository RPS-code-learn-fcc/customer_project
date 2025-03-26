from django.urls import path

# import the necessary views from both apps
from customers.views import *
from app_users.views import *


urlpatterns = [
    # ------------ PATHS TO SHOW DIAGRAMS: ARCHITECTURE, ER DIAGRAM
    path('network-achitecture-diagram/', architecture_diagram_view, name='architecture_diagram'),
    path('orm-diagram/', orm_diagram_view, name='orm_diagram'),
    path('er-diagram/', er_diagram_view, name='er-diagram'),

    path('', landing_page, name='landing-view'), # home page for customers: propmpts user to login
    
    path('home/<str:interests>/', home_view, name='interest'),
    path('home/', home_view, name='home'), # home page for customers: view all customers
    path('search-customers/', search_customers_mailing_list, name='search-customers'),  # AJAX customer search

    path('create-customer/', create_customer_view, name='create_customer_view'),  # main sign-up page
    path('create-customer-partial/', create_customer_partial_view, name='create_customer_view_partial'),  # main sign-up page

    path('create-customer/success/', create_customer_success, name='create_customer_success'),  # Success page after customer is successfully signed up
    path('create-customer/error/', sign_up_error, name='sign_up_error'),  # Error page if customer cannot be signed up
    path('create-customer/skip/', create_customer_skip_step, name='skip_step'), # skip to the next page in the sign up process
    path('cancel_signup/', cancel_signup, name='cancel_signup'), # cancel signup process
    path('cancel-confirmation/', cancel_confirmation, name='cancel_confirmation'), # cofmiration page that the signup page has been added

    path('view-profile/<int:customer_id>', view_full_customer_profile, name='view_customer_profile'),  # main sign-up page
    path('edit-profile/<int:customer_id>', edit_customer, name='edit-customer'),  # main sign-up page
    path('edit-newest-profile/', view_newest_customer_profile, name='view-newest-customer'),  # main sign-up page

    path('search-addresses', search_addresses, name='search-addresses'),
    path('search-phone-numbers', search_phones, name='search-phones'),
    path('search-emails', search_emails, name='search-emails'),
    path('search-documents', search_documents, name='search-documents'),
    path('search-notes', search_notes, name='search-notes'),

    path('<int:customer_id>/toggle-inactive/', toggle_inactive_status, name='toggle_inactive_status'),
    path('create-customer-mailing-list', create_customer_mailing_list, name='create-customer-mailing-list'),
    path('mailing-list/add-selected-address', add_selected_address_list, name='add-selected-address'),
    path('mailing-list/remove-selected-address', remove_selected_address_list, name='remove-selected-address'),

    path("mailing-lists/", list_mailing_lists, name="list-mailing-lists"),
    path("mailing-list/<int:pk>/", view_mailing_list_details, name="view-mailing-list-details"),
    path("mailing-list/<int:pk>/delete", mailing_list_delete_view, name="delete-mailing-list"),
    path("mailing-list/<int:mailing_id>/customer/<int:customer_id>/delete", delete_customer_from_mailing_list, name="delete-customer-mailing-list"),
    path("mailing-list/<int:pk>/edit", mailing_list_edit_view, name="edit-mailing-list"),
    path('mailing-list/<int:mailing_list_id>/print-labels/', print_labels_page, name='print_labels_page'),
    path('mailing-list/<int:mailing_list_id>/generate-labels/', generate_labels_pdf, name='generate_labels_pdf'),    
    path('interest-customer-count/', interest_customer_count, name='interest-customer-count'),


    path('note/<int:customer_id>/<int:note_pk>/', note_detail_view, name='note_detail'),
    path('note/<int:customer_id>/<int:note_pk>/edit/', note_edit_view, name='note_edit'),
    path('notes/<int:customer_id>/view-all/', all_notes_view, name='view-all-notes'),
    path('document/<int:customer_id>/<int:document_pk>/edit/', document_edit_view, name='document_edit'),
    path('document/<int:customer_id>/<int:document_pk>/edit-history/', document_edit_history, name='document_edit_history'),

    path('document/<int:customer_id>/<int:document_pk>/delete/', document_delete_view, name='document_delete'),  
    path('mailing-list/<int:mailing_list_id>/remove/<int:customer_id>/<int:address_id>/', remove_customer_address_from_mailing_list, name='remove_customer_address_from_mailing_list'),
    
    path('address/<int:customer_id>/<int:address_pk>/edit/', address_edit_view, name='address-edit'),
    path('phone/<int:customer_id>/<int:phone_pk>/edit/', phone_edit_view, name='phone-edit'),
    path('email/<int:customer_id>/<int:email_pk>/edit/', email_edit_view, name='email-edit'),

    path('add-address/<int:customer_id>/', add_address, name='customer-add-address'),
    path('add-phone/<int:customer_id>/', add_phone, name='customer-add-phone'),
    path('add-email/<int:customer_id>/', add_email, name='customer-add-email'),
    path('add-note/<int:customer_id>/', add_note, name='customer-add-note'),
    path('add-document/<int:customer_id>/', add_document, name='customer-add-document'),
    path('add-contact-method/', add_contact_method, name='add_contact_method'),

    
    path("address/<int:customer_id>/<int:address_id>/delete", address_delete_view, name="delete-customer-address"),
    path("email/<int:customer_id>/<int:email_id>/delete", email_delete_view, name="delete-customer-email"),
    path("phone/<int:customer_id>/<int:phone_id>/delete", phone_delete_view, name="delete-customer-phone"),


    path('add-interest/', add_interest, name='add-interest'),  
    path('filter-interest/', filter_customers_by_interests, name='filter-customers-by-interests'),  
    path('filter-date/', filter_customers_by_date, name='filter-customers-by-dates'),  
    path('filter-user/', filter_customers_by_users, name='filter-customers-by-users'),  



]