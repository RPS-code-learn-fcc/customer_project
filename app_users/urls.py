from django.urls import path
from app_users.views import *
# from customers.views import *

urlpatterns = [

    path('', profile_view, name="userprofile"), # view the user profile
    path('<str:email_prefix>/', profile_view, name="userprofile-email"),  # View profile by email prefix
    path('<str:email_prefix>/edit/', profile_edit_view, name="userprofile-edit"), # edit profile and provide the email prefix

]