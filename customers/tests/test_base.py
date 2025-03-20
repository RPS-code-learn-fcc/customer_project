from django.test import TestCase, Client
from ..models import *
# Create your tests here.
from django.db import IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist

# imports the custom user model
from django.contrib.auth import get_user_model

# import necessary datetime modules
from datetime import datetime
from datetime import timedelta  
from django.utils import timezone

# import to test image uploads:
from django.core.files.uploadedfile import SimpleUploadedFile  

class HeaderSectionTest(TestCase):
    """Tests the header section"""
    def setUp(self):
        self.client=Client()
        self.user = get_user_model().objects.create_user(email="testuser@test.com", password="testpassword123")
        
    def test_header_section_visible_anonymous_users(self):
        """Header Section Should be visible for anonymous users"""
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200) # ensure page loads correctly
        self.assertContains(response, "<header", html=False)  # Check if <header> exists

    def test_header_visible_authenticated_user(self):
        """Header should be visible for logged-in users"""
        self.client.login(email="testuser@test.com", password="testpassword123")  # Log in user
        response = self.client.get("/customers/home/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<header", html=False)  # Check if <header> exists

    def test_header_contains_expected_links(self):
        """Check if header contains expected links for authenticated users."""
        # Log in the user
        self.client.login(email="testuser@test.com", password="testpassword123")

        # Make the request after logging in
        response = self.client.get("/customers/home/")

        # Check for expected content in the response
        self.assertContains(response, "My Company")  # Check for company name
        self.assertContains(response, "Log Out")  # Check for logout link
            
    def test_header_contains_login_link_for_anonymous_users(self):
        """Check if header contains 'Log In' link and redirects to login page for anonymous users."""
        # Make the request as an anonymous user and follow the redirect
        response = self.client.get("/customers/home/", follow=True)

        # Check for the "Log In" link in the header of the final response
        self.assertContains(response, "Log In")  # Check for login link

        # Verify that the initial response was a redirect to the login page
        self.assertEqual(response.redirect_chain[0][1], 302)  # Check for redirect status code
        self.assertIn("/accounts/login/?next=/customers/home/", response.redirect_chain[0][0])  # Check redirect URL

class SecondaryHeaderTest(TestCase):
    def setUp(self):
        """Setup creates a test client & test user"""
        self.client = Client()
        self.user = get_user_model().objects.create_user(email="user@test.com", password="testpassword")

    def test_secondary_header_hidden_anonymous_users(self):
        """Secondary Header should NOT be visible for anonymous users on the landing page"""
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<nav", html=False)  # Ensure no extra header for anonymous users

    def test_secondary_header_visible_logged_in_users(self):
        """Secondary Header should be visible for authenticated users"""
        self.client.login(email="user@test.com", password="testpassword")  # Log in the user
        response = self.client.get("/customers/home/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<nav", html=False)  # Check if the secondary header is present
        
    def test_secondary_header_contains_expected_links(self):
        """Check if secondary header contains expected elements for logged-in users"""
        self.client.login(email="user@test.com", password="testpassword")
        response = self.client.get("/customers/home/")
        self.assertEqual(response.status_code, 200)

        # Check for navigation links
        self.assertContains(response, '<a href="/customers/create-customer/">Create Customer</a>', html=True)
        self.assertContains(response, '<a href="/profile/user/">My Profile</a>', html=True)


class HeroSectionTest(TestCase):
    """Tests that the hero block shows up for anonymous users only"""
    def setUp(self):
        """setup creates a test client & test user"""
        self.client = Client()
        self.user = get_user_model().objects.create_user(email="user@test.com", password="testpassword")
        
    def test_hero_section_visible_anonymous_users(self):
        """Hero Section Should be visible for anonymous users only"""
        response = self.client.get("/customers/") # sends get request to URL
        self.assertContains(response, "hero")  # the response should have a hero
         
    def test_hero_section_invisible_for_logged_in_users(self):
        """Hero section should be hidden for logged-in users"""
        self.client.login(email="user@test.com", password="testpassword")  # Log in a user
        response = self.client.get("/customers/home/")
        self.assertNotContains(response, "hero")  # Ensure the hero section is not present
        
    def test_hero_section_not_shown_on_login_page(self):
        """Hero section should NOT be shown on the login page"""
        response = self.client.get("/accounts/login/")  # Request the login page
        self.assertNotContains(response, "hero")  # Hero section should not be present

    def test_redirects_resolved_properly(self):
        """Ensure URL redirects are properly resolved (301 redirects) - goes to login page and no hero is shown"""
        response = self.client.get("/customers/home/", follow=True)  # Missing trailing slash
        self.assertEqual(response.status_code, 200)  # Should resolve and return 200
        self.assertNotContains(response, "hero")  # Hero section should not be present

    
    def test_hero_section_does_not_break_page(self):
        """Ensure hero section does not cause template rendering errors"""
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)  # Ensure page loads correctly
        
    def test_footer_included_for_all_users(self):
            """Footer should be included for all users (anonymous and authenticated)."""
            # Test for anonymous users
            response = self.client.get("/customers/")
            self.assertContains(response, "<footer", html=False)  # Check if <footer> exists

            # Test for authenticated users
            self.client.login(email="user@test.com", password="testpassword")
            response = self.client.get("/customers/home/")
            self.assertContains(response, "<footer", html=False)  # Check if <footer> exists
            
