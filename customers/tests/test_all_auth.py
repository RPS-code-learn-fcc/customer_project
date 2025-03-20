from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Get my user model which is CustomUser
User = get_user_model()

class AllauthLoginTests(TestCase):
    def setUp(self):
        """Set up a valid user"""
        self.user = User.objects.create_user(
            email='testuser@email.com',
            password='testpassword123'
        )

    def tearDown(self):
        """Clean up the test user after each test"""
        # Delete the test user
        self.user.delete()

    def test_successful_login(self):
        """Tests the login functionality of django allauth"""
        login_url = reverse('account_login')

        # Attempt to log in
        response = self.client.post(
            login_url,
            {
                'login': 'testuser@email.com',
                'password': 'testpassword123',
            }
        )
        # The user should be redirected after successful login
        self.assertEqual(response.status_code, 302, msg="status code 302 indicates a successful redirect")  
        self.assertRedirects(response, reverse('home')) 

        # User should be authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_login_invalid_credentials(self):
        """Tests the login functionality of django allauth with invalid credentials"""
        
        # Attempt to log in with invalid credentials
        response = self.client.post(
            reverse('account_login'),
            {
                'login': 'testuser@email.com',
                'password': 'invalidpassword123',
            }
        )

        # Check if the response contains the correct error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The email address and/or password you specified are not correct.")

    def test_login_inactive_user(self):
        """Tests that an inactive user cannot successfully login to the application"""
        
        # Deactivate the user
        self.user.is_active = False
        self.user.save()

        # Attempt to log in
        response = self.client.post(
            reverse('account_login'),
            {
                'login': 'testuser@email.com',
                'password': 'testpassword123',
            },
            follow=True  # Follow the redirect
        )

        # Check if the response contains the error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This account is inactive.")
        
class LogoutTestCase(TestCase):
    def setUp(self):
        """Create a test user and log them in."""
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="securepassword123"
        )
        self.client.login(email="test@example.com", password="securepassword123")  # Log the user in

    def test_logout_view(self):
        """Test if the user can log out successfully."""
        # make sure the user is logged in before logging out
        response = self.client.get(reverse("account_logout"))  # GET request to logout page
        self.assertEqual(response.status_code, 200)  # make sure logout page loads

        # Perform the actual logout action
        response = self.client.post(reverse("account_logout"))  # POST request to logout
        self.assertRedirects(response, reverse("landing-view"))  # Should redirect to login page

        # make sure the user is actually logged out
        response = self.client.get(reverse("account_logout"))  # Try accessing logout again
        self.assertFalse("_auth_user_id" in self.client.session)  # Check session to confirm logout
    def test_logout_when_not_logged_in(self):
        """Test if logout works properly when user is not logged in."""
        self.client.logout()  # make sure the user is logged out

        # Attempt to access logout page
        response = self.client.get(reverse("account_logout"))

        # Check if the response is a redirect (unauthenticated users may be redirected)
        self.assertIn(response.status_code, [200, 302])  # Allow 302 (redirect) or 200 (page load)

        # If redirected, check where it's redirecting to
        if response.status_code == 302:
            self.assertRedirects(response, reverse("landing-view"))  # Expected redirect location

        # Attempt to log out via POST (should still redirect)
        response = self.client.post(reverse("account_logout"))
        self.assertRedirects(response, reverse("landing-view"))  # Should redirect after logout


    def test_logout_requires_post(self):
        """make sure logout is only performed via POST request."""
        self.client.login(email="test@example.com", password="securepassword123")  # Log user in

        # Attempt to log out using a GET request
        response = self.client.get(reverse("account_logout"))
        self.assertEqual(response.status_code, 200)  # Should just load the logout page, not log out

        # Confirm user is still logged in
        self.assertTrue("_auth_user_id" in self.client.session)

        # Now attempt with a POST request (which should log the user out)
        response = self.client.post(reverse("account_logout"))
        self.assertRedirects(response, reverse("landing-view"))  # Redirect after logout

        # Confirm user is logged out
        self.assertFalse("_auth_user_id" in self.client.session)

class AllauthSignupTests(TestCase):
    
    def test_successful_user_registration(self):
        """Tests that a new user can successfully register using Django Allauth"""
        signup_url = reverse('account_signup')  # URL for Allauth signup
        # Data for the new user
        user_data = {
            'email': 'newuser@example.com',
            'password1': 'securepassword123',  # Password
            'password2': 'securepassword123',  # Password confirmation
        }

        # Attempt to register the new user
        response = self.client.post(signup_url, user_data)

        # Check if the user was created in the database
        new_user = User.objects.filter(email='newuser@example.com').first()
        self.assertIsNotNone(new_user, msg="New user should be created in the database")

        # Check if the user is active (no email verification required)
        self.assertTrue(new_user.is_active, msg="New user should be active immediately")
    
    def test_failed_user_registration_invalid_data(self):
        
        """Tests that a user cannot register with invalid or missing data"""
        signup_url = reverse('account_signup')  # URL for Allauth signup

        # Invalid data (missing email)
        invalid_user_data = {
            'password': 'securepassword123',  # Only one password field
        }

        # Attempt to register the new user with invalid data
        response = self.client.post(signup_url, invalid_user_data)

        # The form should be re-rendered with errors (status code 200)
        self.assertEqual(response.status_code, 200, msg="status code 200 indicates form errors")

        # Check if the response contains an error message
        self.assertContains(response, "This field is required.", msg_prefix="Form should display an error for missing email")

        # make sure no user was created in the database
        new_user = User.objects.filter(email='newuser@example.com').first()
        self.assertIsNone(new_user, msg="No user should be created with invalid data")
        
class AllauthPasswordResetTests(TestCase):
    def test_password_reset_redirects_to_home(self):
        """Tests that accessing the password reset page redirects to the home page"""
        # Create a user
        User = get_user_model()
        user = User.objects.create_user(
            email='test@test.com',  # make sure this matches the login credentials
            password='testpass123'
        )

        # Log the user in
        login_successful = self.client.login(email='test@test.com', password='testpass123')
        self.assertTrue(login_successful, "User should be logged in")

        # URL for the password reset page
        password_reset_url = reverse('account_reset_password')
        # Access the password reset page
        response = self.client.get(password_reset_url, follow=True)  # Follow the redirect

        # The user should be redirected to the home page
        self.assertEqual(response.status_code, 200, msg="status code 200 indicates the final page after redirect")
        self.assertRedirects(response, '/customers/home/', status_code=302, target_status_code=200)