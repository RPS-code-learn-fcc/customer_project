"""
URL configuration for customer_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include



"""
    Import the necessary views from the customers & app_users apps
"""
from customers.views import *
from app_users.views import *


"""
    Make sure static files can be served during development
"""
from django.conf import settings
from django.conf.urls.static import static 

"""
    Imported for redirects of urls
"""
from django.shortcuts import redirect
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('customadmin/', admin.site.urls),
    # redirect other allauth urls that will not be used to the home page
    path("accounts/email/", lambda request: redirect("/customers/home"), name="account_email"),
    path("accounts/password/reset/", RedirectView.as_view(url="/customers/home", permanent=False), name="account_reset_password"),
    

    # include other django all auth urls: login code, etc. for project
    path("accounts/", include("allauth.urls")),
    
    # include other app urls
    path('customers/', include('customers.urls')),
    path('profile/', include('app_users.urls')),
    
    # Redirect root URL (http://127.0.0.1:8000/) to customers/
    path('', RedirectView.as_view(url='/customers/', permanent=True)),
    
]




# Serve media files during development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
