# Create tests based on unittest.TestCase
from django.test import TestCase

# imoprt necessary datetime modules
from datetime import datetime
from datetime import timedelta  
from django.utils import timezone


# import the necessary models from both apps: 
from app_users.models import CustomUser
from customers.models import CustomerInterest

# import the necessary forms:
from .forms import EditCustomUserForm

# import exceptions
from django.core.exceptions import ValidationError

# import to test image uploads:
from django.core.files.uploadedfile import SimpleUploadedFile  

# import to check if an uploaded image is an instance of django's ImageFieldFile
from django.db.models.fields.files import ImageFieldFile  

# import to do user testing
from django.urls import reverse

# write a django TestCase for the CustomUser Model
class CustomUserTestCase(TestCase):
    """
        Tests the CustomUser model - validation, that new instances of the model can be saved correctly, etc.
    """
    def setUp(self):
        """SetUp method is called before each unit test."""
        self.email = "test@test.com"
        self.password = "passwordtest"
        
        self.email_admin = "admin@test.com"
        self.password_admin = "passwordtestadmin"
             
        self.valid_image = SimpleUploadedFile("test_image.jpg", b"image_data", content_type="image/jpeg")  
        self.valid_image_jpg = SimpleUploadedFile("test_image.jpg", b"image_data", content_type="image/jpg")  
        self.invalid_image = SimpleUploadedFile("test_image.txt", b"image_data", content_type="text/plain")
        self.invalid_image_png =  SimpleUploadedFile("test_image.png", b"image_data", content_type="image/png")  
        self.invalid_image_gif =  SimpleUploadedFile("test_image.png", b"image_data", content_type="image/gif")  
        
        self.interest = CustomerInterest.objects.create(name="Tree Sale", slug="tree-sale")
        self.interest2 = CustomerInterest.objects.create(name="Soil Tests", slug="soil-tests")
        self.interest3 = CustomerInterest.objects.create(name="Summer Camp", slug="summer-camp")

    def test_create_user_successful(self):
        """Tests that a regular user can be created with an email and password"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)   
        
        self.assertEqual(user.email, self.email, msg="The user instance email should be equal to the amil provided.")
        self.assertTrue(user.check_password(self.password), msg="The user instance password should be equal to the password provided.")

        self.assertFalse(user.is_staff, msg="A regular user should not have access to the admin panel.")
        self.assertFalse(user.is_superuser, msg="A regular user should not be a superuser / have admin permissions.")
        
    def test_user_without_email(self):
        """Test that creating a regular user without an email creates a value error"""
        with self.assertRaises(ValueError): # invalid data type
            CustomUser.objects.create_user(email=None, password=self.password)
    
    def test_user_without_password(self):  
        """Test that creating a regular user with password=None sets an unusable password"""  
        user = CustomUser.objects.create_user(email=self.email, password=None)  
        self.assertFalse(user.has_usable_password(), msg="A password of none should not create a usable password.")
    
    def test_create_superuser_successful(self):
        """Tests that a superuser can be created with an email and password"""
        user = CustomUser.objects.create_superuser(email=self.email_admin, password=self.password_admin)   
        
        self.assertEqual(user.email, self.email_admin, msg="The user instance email should match the admin email.")
        self.assertTrue(user.check_password(self.password_admin), msg="The user instance password should match the admin password.")
        self.assertTrue(user.is_staff, msg="The created user should have access to the admin panel.")
        self.assertTrue(user.is_superuser, msg="The created user should be a superuser")
        
    def test_super_user_without_email(self):
        """Test that creating a super user without an email creates a value error"""
        with self.assertRaises(ValueError): # invalid data type
            CustomUser.objects.create_superuser(email=None, password=self.password_admin)
    
    def test_super_user_without_password(self):  
        """Test that creating a super user with password=None sets an unusable password"""  
        user = CustomUser.objects.create_superuser(email=self.email_admin, password=None)  
        self.assertFalse(user.has_usable_password(), msg="A password of none should not create a usable password.")
            
    def test_create_user_default_is_active(self):
        """ Tests that a regular user can be created as an active user"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)   
        self.assertEqual(user.email, self.email, msg="The user should exist.")
        self.assertTrue(user.check_password(self.password), msg="The user should have a password.")
        self.assertTrue(user.is_active, msg="A newly created regular user should be an active user.")
    
    def test_create_superuser_default_is_active(self):
        """ Tests that a super user can be created as an active user"""
        user = CustomUser.objects.create_superuser(email=self.email_admin, password=self.password_admin)   
        self.assertEqual(user.email, self.email_admin, msg="The superuser should exist.")
        self.assertTrue(user.check_password(self.password_admin), msg="The superuser should have a password.")
        self.assertTrue(user.is_active, msg="A newly created super user should be an active user.")
    
    def test_date_joined_regular_user(self):
        """Tests that the date_joined field is set to the current date and time for a regular user"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password) 
        self.assertAlmostEqual(user.date_joined, timezone.now(), delta=timedelta(seconds=1), msg="The time that the user joined should be within 1 second of the current time.")
    
    def test_date_joined_superuser(self):
        """Tests that the date_joined field is set to the current date and time for a super user"""
        user = CustomUser.objects.create_superuser(email=self.email_admin, password=self.password_admin) 
        self.assertAlmostEqual(user.date_joined, timezone.now(), delta=timedelta(seconds=1), msg="The time that the user joined should be within 1 second of the current time.")

    def test_date_joined_is_date(self):
        """Tests that the date_joined field is a date time"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        self.assertIsInstance(user.date_joined, datetime, msg="The user date_joined field should be an instance of datetime")
    
    def test_last_login_is_null_for_new_users(self):
        """Tests that the last_login field for a newly created regular user is None"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        self.assertIsNone(user.last_login, msg="The last_login field should be null for a newly created user that has never logged in.")
    
    def test_last_login_updated_login_success(self):
        """Tests that the last_login field is updated after a successful user login"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        
        # checks that upon user creation, last login is none:
        self.assertIsNone(user.last_login,  msg="The last_login field should be null for a newly created user that has never logged in.")
        
        # login the newly created user
        self.client.login(email=self.email, password=self.password)
        
        # refresh the user object to get last_login
        user = CustomUser.objects.get(email=self.email)
        
        # check that last_login is no longer null but contains a value 
        self.assertIsNotNone(user.last_login,  msg="The last_login field should now be updated to a non-null value for a user that has logged in.")
        
        # check that the newly created last_login is a datetime instance
        self.assertIsInstance(user.last_login, datetime,  msg="The last_login field should be a datetime instance.")
        
    def test_last_login_not_updated_failed_login(self):
        """Tests that the last_login field is not updated after an unsuccessful attempt at user login"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        
        # checks that upon user creation, last login is none:
        self.assertIsNone(user.last_login)
        
        # login the newly created user with wrong password
        self.client.login(email=self.email, password="incorrecttestpassword")
        
        # check that last_login is still null  
        self.assertIsNone(user.last_login,  msg="The last_login field should be null for a user that has never logged in.")
        
    def test_successful_image_upload(self):
        """Tests that an image can be successfully uploaded to the db"""
        user = CustomUser.objects.create_user(email="email@email.com", password=self.password)
        # create a mock image using SinpleUploadedFile(file name, string of bytes/content of file, MIMIEtype of file)
        image = SimpleUploadedFile("test_image.jpg", b"image_data", content_type="image/jpeg")
        
        # save the image to the user image field
        user.image = image
        user.save()
        self.assertIsNotNone(user.image, msg="The image field should not be none when an image has been uploaded")
        self.assertIsInstance(user.image, ImageFieldFile, msg="The image field should be an instance of ImageFieldFile")
        self.assertIn('test_image', user.image.name, msg="The uploaded file name should be in the user image field name")

        
    def test_successful_image_retrival(self):
        """Tests that an uploaded image can be successfully retrieved and displayed correctly."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password, image=self.valid_image)
        self.assertIsNotNone(user.image, msg="The user image field should not be none.")
        retrieved_image = CustomUser.objects.get(email=self.email).image  
        self.assertEqual(retrieved_image, user.image, msg="The retrieved image should equal the image user field.")
        
        
    def test_blank_image_values_allowed(self):
        """Tests that blank image values are allowed."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)

        # do not add an image and make make sure the ImageFieldFile's name is none
        self.assertEqual(user.image.name, '', msg="If no image is saved to the user instance, it is equal to a blank field.")
    
    def test_invalid_image_type_cannot_be_saved_to_image_field(self):
            # Create a user instance
            user = CustomUser(email=self.email, password =self.password, image=self.invalid_image)

            # Assert that validation fails
            with self.assertRaises(ValidationError):
                user.full_clean()  # This method triggers model field validations
        
    def test_img_uploaded_jpeg_jpg_only(self):  
        """Tests that uploaded image is only in permissible formats: jpeg or jpg."""  
        # Create a user instance  
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        
        # Test with a valid JPEG file  
        user.image = self.valid_image  
        try:  
            user.full_clean()  
        except ValidationError:  
            self.fail('Invalid Image file. Upload a valid Jpg or jpeg file.')  
        
        # Test with a valid JPG file  
        user.image = self.valid_image_jpg 
        try:  
            user.full_clean()  
        except ValidationError:  
            self.fail('Invalid Image file. Upload a valid Jpg or jpeg file.')  
        
        # Test with an invalid PNG file  
        user.image = self.invalid_image_png
        with self.assertRaises(ValidationError):  
            user.full_clean()  
        
        # Test with an invalid GIF file   
        user.image = self.invalid_image_gif  
        with self.assertRaises(ValidationError):  
            user.full_clean()

    
    def test_successful_addition_bio_field_to_user(self):
        """Tests that a bio can be successfully added to a user instance"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password, bio="This is a new bio.")
        self.assertIsNotNone(user.bio, msg="The user bio field should not be none.")
        self.assertEqual(user.bio, "This is a new bio.")
    
    def test_no_bio_addition_reverts_to_default(self):
        """Tests that if there is no bio uploaded - it defaults to the bio provided."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password) 
        self.assertEqual(user.bio, "The lack of power to take joy in outdoor nature is as real a misfortune as the lack of power to take joy in books. --T. Roosevelt.", "Bio Field does not match expected default bio.")
    
    def test_successful_addition_job_title_field_to_user(self):
        """Tests that a Job Title can be successfully added"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password, job_title="Administrative Assistant")
        self.assertIsNotNone(user.job_title, msg="The job title should not be none.")
        self.assertEqual(user.job_title, "Administrative Assistant", msg="The user instance job title should be equal to the job title provided.")
    
    def test_no_job_title_addition_reverts_to_default(self):
        """Tests that if there is no job title uploaded - it defaults to the one provided."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password) 
        self.assertEqual(user.job_title, "Conservation Specialist", msg="The user instance job title should be equal to the default job title when none is provided.")
    
    def test_invalid_job_title(self):
        """Tests validation for Job title."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password, job_title="1564 z&!") # job title cannot contain special characters
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_invalid_bio(self):
        """Tests validation for Job bio that is too long."""
        # job title cannot be longer than 500 characters
        user = CustomUser.objects.create_user(email=self.email, password=self.password, bio="Theodore Roosevelt, the 26th President of the United States (1901–1909), was a dynamic and influential leader whose legacy encompasses politics, conservation, and a deep commitment to public service. Born on October 27, 1858, in New York City, Roosevelt overcame childhood illness to become a robust advocate for the strenuous life. His political career included roles as a New York State Assemblyman, Assistant Secretary of the Navy, and Governor of New York. Following President McKinley's assassination, Roosevelt assumed the presidency at age 42, becoming the youngest U.S. president. Known for his progressive policies, he championed the Square Deal, focusing on trust-busting, fair labor practices, and consumer protections. A passionate conservationist, Roosevelt established the U.S. Forest Service, created five national parks, and protected over 230 million acres of public land. Beyond politics, he was a prolific writer, naturalist, soldier, and explorer. His adventurous spirit was evident in leading the Rough Riders during the Spanish-American War and later embarking on expeditions to Africa and South America. Roosevelt's indomitable energy, reformist zeal, and larger-than-life persona made him one of America's most iconic leaders.") 
        with self.assertRaises(ValidationError):
            user.full_clean()
        
    def test_no_first_name_and_last_name_allowed(self):
        """Tests that a new user object can be created without a first_name and last_name, as email is required and contains this information."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password) 
        self.assertEqual(user.first_name, '', msg="An empty first name is allowed as a default.")
        self.assertEqual(user.last_name, '',  msg="An empty last name is allowed as a default.")
       

    def test_first_name_valid(self):
        """Tests that valid first names and business names are accepted."""
        valid_first_names = ["John", "Melva", "Big-Lots", "13 Candles", "Big Run Farms"]
        user = CustomUser.objects.create_user(email=self.email, password=self.password)

        for name in valid_first_names:
            user.first_name = name
            try:
                user.full_clean()
            except ValidationError:
                self.fail(f"Invalid first name: {name}")
    
    def test_last_name_valid(self):
        """Tests that valid last names accepted."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)

        valid_last_names = ["Smith", "Smith-Johnson", "Kelley"]
        for name in valid_last_names:
            user.last_name = name
            try:
                user.full_clean()
            except ValidationError:
                self.fail(f"Invalid first name: {name}")
  
    def test_first_name_invalid(self):  
        """Tests that invalid first names are not accepted."""  
        invalid_first_names = ["John(&&)", "123@@#", "!!!"]  
        user = CustomUser.objects.create_user(email=self.email, password=self.password)  
        
        for name in invalid_first_names:  
            user.first_name = name  
            with self.assertRaises(ValidationError):  
                user.full_clean()
    
    def test_last_name_invalid(self):  
        """Tests that invalid first names are not accepted."""  
        invalid_last_names = ["Smith&123", "123456", "!!!"]  
        user = CustomUser.objects.create_user(email=self.email, password=self.password)  
        
        for name in invalid_last_names:  
            user.last_name = name  
            with self.assertRaises(ValidationError):  
                user.full_clean()


    def test_add_interest_to_user(self):
        """Test to successfully interests to the user"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        # add interests to the user
        user.interests.add(self.interest, self.interest2, self.interest3)
        
        # check that the interests are in the user.intersts field
        self.assertIn(self.interest, user.interests.all(), msg="Interest1 is successfully added to the user instance.")
        self.assertIn(self.interest2, user.interests.all(), msg="Interest2 is successfully added to the user instance.")
        self.assertIn(self.interest3, user.interests.all(), msg="Interest3 is successfully added to the user instance.")
        
        interests = user.interests.all()
        self.assertEqual(interests.count(), 3, msg="The user instance should have 3 interests.")

        
    def test_reverse_relationship(self):
        """Test reverse relationship between CustomUser and CustomerIntersts"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        user2 = CustomUser.objects.create_user(email=self.email_admin, password=self.email_admin)

        user.interests.add(self.interest, self.interest2, self.interest3)
        user2.interests.add(self.interest, self.interest3)

        all_users_with_interest = self.interest.users_with_interest.all()
        all_users_with_interest2 = self.interest2.users_with_interest.all()

        self.assertEqual(all_users_with_interest.count(), 2 , msg="The user instance should have 2 users witi interest 1.")
        self.assertEqual(all_users_with_interest2.count(), 1, msg="The user instance should have 1 user with interest 2.")

    def test_no_interests(self):
        """Test that checks if a user has no interests"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        self.assertEqual(user.interests.count(), 0)
        
    def test_cannot_add_identical_interests(self):
        """Test that verifies that the many to many field does not allow duplicates in the interests field for Users"""
        
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        user.interests.add(self.interest, self.interest)
        user.save()
        
        self.assertEqual(user.interests.count(), 1, msg="Only one interest can be added.")
        self.assertEqual(user.interests.first(), self.interest, msg="The first interest should be the interest successfully added.")
        
    def test_get_full_name(self):
        """Test the get_full_name method"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password, first_name="Mary", last_name="Smith")
        self.assertEqual(user.get_full_name(), "Mary Smith", msg="get_full_name method should equal 'Mary Smith'")
        
    def test_short_name(self):
        """Test the short_name method"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        self.assertEqual(user.short_name(), "test", msg="short_name method shoudl return 'test' email prefix")
    
    def test_profile_image_property(self):
        """Test the profile_image property - retrives the url of the associated profile image or the default profile image."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password)
        user.image = self.valid_image 
        self.assertEqual(user.profile_image, "/media/test_image.jpg", msg="The uploaded mock image should match the test image stored in 'media/")
        
        valid_image = ''  
        user.image = valid_image  
        self.assertEqual(user.profile_image, "/static/images/default_profile_image.jpg", msg="If a blank image is uploaded, the default profile image will be used")
        
    def test_user_name(self):
        """Tests the user_name property"""
        user = CustomUser.objects.create_user(email=self.email, password=self.password, first_name="Mary", last_name="Smith")
        self.assertEqual(user.user_name, "Mary Smith", msg="user_name method should return 'Mary Smith' if first and last name are provided.")
    
        user = CustomUser.objects.create_user(email="test_email@test.com", password=self.password, first_name="", last_name="")
        self.assertEqual(user.user_name, "test_email", msg="user_name method should return 'test_email' (email prefix) if first and last name are not provided.")

def test_time_since_joined_property(self):
        """Tests the Time Since Joined Property."""
        user = CustomUser.objects.create_user(email=self.email, password=self.password, first_name="Mary", last_name="Smith")
  
        # Calculate expected result using Django's timesince function
        expected_time_since_joined = timezone.timesince(user.date_joined)

        # Verify the property returns the expected result
        self.assertEqual(
            user.time_since_joined,
            expected_time_since_joined,
            msg="time_since_joined property should return the correct time difference."
        )
        
# ------------------- TEST THE VIEWS FOR APP_USERS APP ---------------------
class AppUsersViewTest(TestCase):
    def setUp(self):
        """Set Up an Enviornment with Three Users and three interests"""
        self.user1 = CustomUser.objects.create_user(email="user1@test.com", password="testpassword1", first_name="First", last_name="Last")
        self.user2 = CustomUser.objects.create_user(email="user2@test.com", password="testpassword2", first_name="Second", last_name="Last")
        self.user3 = CustomUser.objects.create_user(
            email="user3@test.com",
            password="testpassword3",
            bio="I love long walks on the beach.",
            job_title="Watershed Coordinator"
        )
        self.interest = CustomerInterest.objects.create(name="Tree Sale", slug="tree-sale")
        self.interest2 = CustomerInterest.objects.create(name="Soil Tests", slug="soil-tests")
        self.interest3 = CustomerInterest.objects.create(name="Summer Camp", slug="summer-camp")
        self.user3.interests.add(self.interest, self.interest2)
   

    def test_logged_in_user_view_profile(self):
        """Test that a logged in user can view their own profile."""
        # log a user in:
        self.client.force_login(self.user1)
        # checks that the successfuly view returns an Http success code: 200
        response = self.client.get(reverse('userprofile'))
        
        # return an Http success code: 200
        self.assertEqual(response.status_code, 200, msg="The logged in user can view their own profile, returning a 200 success code.")
        
        # check if the context being passed is the same as the created user1's profile in test.py
        self.assertEqual(response.context['profile'], self.user1, msg="User1's information should be passed in the context variable 'profile' to the template. ")
        
        # check the template used in the response is as it should 
        self.assertTemplateUsed(response, 'app_users/view_userprofile.html')
        
         
    def test_logged_in_user_view_another_profile(self):
        """Test that a logged in user can view another user's profile by email prefix."""
        # log a user in:
        self.client.force_login(self.user1)
        
        # check that they can view their own profile
        response = self.client.get(reverse('userprofile-email', kwargs={'email_prefix': 'user2'}))

        # checks that the successfuly view returns an Http success code: 200
        self.assertEqual(response.status_code, 200, msg="A 200 success status code should be returned by the response when a user tries to view a user profile by email prefix.")
        
        # check if the context being passed is the same as the created user2's profile in test.py
        self.assertEqual(response.context['profile'], self.user2, msg="User2's information should be passed in the context variable 'profile' to the template.")
        
        # check the template used in the response is as it should be
        self.assertTemplateUsed(response, 'app_users/view_userprofile.html')
    
    def test_logged_in_user_view_their_profile(self):
        """Test that a logged in user can view their own profile using the email prefix."""
        # log a user in:
        self.client.force_login(self.user1)
        
        # check that they can view their own profile
        response = self.client.get(reverse('userprofile-email', kwargs={'email_prefix': 'user1'}))

        # checks that the successfuly view returns an Http success code: 200
        self.assertEqual(response.status_code, 200, msg="A 200 success status code should be returned by the response when a user tries to view their own user profile by email prefix.")
        
        # check if the context being passed is the same as the created user1's profile in test.py
        self.assertEqual(response.context['profile'], self.user1)
        
        # check the template used in the response is as it should be
        self.assertTemplateUsed(response, 'app_users/view_userprofile.html')
        
    def test_logged_in_user_cannot_view_profile_does_not_exist(self):
        """Test that a logged in user cannot view a customer's profile that does not exist.."""
        # log a user in:
        self.client.force_login(self.user1)
        
        # check that they can view their own profile
        response = self.client.get(reverse('userprofile-email', kwargs={'email_prefix': 'user4'}))

        # checks that the successfuly view returns an Http success cannot be found code for user4's nonexistent code: 404
        self.assertEqual(response.status_code, 404, msg="A 404 response code should be returned if a logged in user attempts to view a profile that doesn't exist.")
        
        # will use custom 404 page.
        self.assertTemplateUsed(response, '404.html')
    
    def test_non_logged_in_user_cannot_view_profile(self):
        """Test that shows that it is forbidden for an anonymous user to view another user's profile."""
        
        # no login - checks that they cannot view a profile
        response = self.client.get(reverse('userprofile-email', kwargs={'email_prefix':'user1'}))
        
        # redirection response code
        self.assertEqual(response.status_code, 302, msg="An anonymous user attempting to view another user's profile should be redirected - response code 302.")
    
    def test_non_logged_in_user_cannot_edit_profile(self):
        """Test that shows that it is forbidden for a non-logged in user to edit another user's profile."""
        
        # no login - checks that they cannot view a profile
        response = self.client.get(reverse('userprofile-edit', kwargs={'email_prefix':'user1'}))
        
        # redirection response we
        self.assertEqual(response.status_code, 302, msg="An anonymous user attempting to edit a user's profile should be redirected - response code 302.")
    
    def test_logged_in_user_cannot_edit_another_users_profile(self):  
        """Test that a logged-in user cannot edit another user's profile."""  
        # Log in a user  
        self.client.force_login(self.user3)  
            
        # Attempt to edit another user's profile  
        response = self.client.get(reverse('userprofile-edit', kwargs={'email_prefix': 'user2'}))  
            
        # Test that the HttpResponseForbidden response is returned  
        self.assertEqual(response.status_code, 403, msg="It is forbidden for a logged in user to view another user's profile - response could 403 should be returned.")
        
        # checks that the message has changed to the following message
        self.assertIn(b"You do not have permission to edit this page.", response.content, msg="A message should be displayed to the user if they attempt to view a forbidden page.")
        
    def test_user_can_view_profile_edit_page(self):
        """Test that a logged-in user can view their profile edit page."""
        self.client.force_login(self.user3)

        response = self.client.get(reverse('userprofile-edit', kwargs={'email_prefix': 'user3'}))
        
        self.assertEqual(response.status_code, 200, msg="A user can view their edit profile page successfully- status code 200 is returned.")
        self.assertTemplateUsed(response, 'app_users/edit_userprofile.html')
        self.assertEqual(response.context['profile'], self.user3)
        
    def test_form_validation_for_profile_update(self):
        """Test that the form validates correctly for valid data."""
        updated_bio = "This is my updated Bio."
        updated_title = "Job Title"
        new_image = SimpleUploadedFile("new_pic.jpg", b"image_data", content_type="image/jpeg")

        form_data = {'bio': updated_bio, 'job_title': updated_title, 'image': new_image}
        form = EditCustomUserForm(data=form_data, instance=self.user3)

        self.assertTrue(form.is_valid(), msg="The form should be valid - True.")
        
    def test_form_saves_correctly(self):
        """Test that the form saves the data correctly to the user instance."""
        updated_bio = "This is my updated Bio."
        updated_title = "Job Title"
        new_image = SimpleUploadedFile("new_pic.jpg", b"image_data", content_type="image/jpeg")

        form_data = {'bio': updated_bio, 'job_title': updated_title, 'image': new_image}
        form = EditCustomUserForm(data=form_data, instance=self.user3)

        if form.is_valid():
            form.save()

        # Refresh user object and verify changes
        self.user3.refresh_from_db()
        self.assertEqual(self.user3.bio, updated_bio, msg="The user bio field should match the expected updated_bio string.")
        self.assertEqual(self.user3.job_title, updated_title, msg="The user job title field should match the expected updated_title string.")
        self.assertAlmostEqual(self.user3.profile_updated, timezone.now(), delta=timedelta(seconds=1), msg="The updated profile time should be within one second of the current time.")

        self.assertIsNotNone(self.user3.image, msg="The image value should not be None but always contain an image: default image or uploaded image.")
        
    def test_user_can_update_profile(self):
        """Test that a logged-in user can update their profile."""
        self.client.force_login(self.user3)

        updated_bio = "This is my updated Bio."
        updated_title = "Job Title"

        response = self.client.post(
            reverse('userprofile-edit', kwargs={'email_prefix': 'user3'}),
            data={
                'bio': updated_bio,
                'job_title': updated_title,
            }
        )

        # Ensure the response redirects after saving
        self.assertEqual(response.status_code, 302, msg="Response code of 302 after successfully editing user profile and saving it.")
        self.assertRedirects(response, reverse('userprofile-email', kwargs={'email_prefix': 'user3'}))

        # Refresh user object and verify changes
        self.user3.refresh_from_db()
        self.assertEqual(self.user3.bio, updated_bio)
        self.assertEqual(self.user3.job_title, updated_title)
        
    def test_user_can_update_interests(self):
        """Test that a logged-in user can update their interests."""
        self.client.force_login(self.user3)

        # Check initial interests
        self.assertIn(self.interest, self.user3.interests.all())
        self.assertIn(self.interest2, self.user3.interests.all())
        self.assertNotIn(self.interest3, self.user3.interests.all())

        # Prepare data to add interest3
        # id is required to add ManyToManyField Relationships - should be stored as list of ids
        updated_interests = [self.interest.id, self.interest2.id, self.interest3.id]
        response = self.client.post(
            reverse('userprofile-edit', kwargs={'email_prefix': 'user3'}),
            data={
                'bio': self.user3.bio,  # Include existing data to avoid validation issues
                'job_title': self.user3.job_title,
                'interests': updated_interests,  # Update interests
            }
        )

        # Ensure the response redirects after saving
        self.assertEqual(response.status_code, 302, f"Response didn't redirect as expected: {response.status_code}")

        # Refresh user object and verify updated interests
        self.user3.refresh_from_db()
        self.assertIn(self.interest3, self.user3.interests.all())
        self.assertEqual(len(self.user3.interests.all()), 3)  # Ensure all 3 interests are present

# ------------------- TEST THE LOGIN & LOGOUT USING DJANGO-ALLAUTH ------------------
class UserLoginTestCase(TestCase):
    """Test case for user authentication using Django-Allauth."""

    def setUp(self):
        """Set up a test user with email-based authentication and reset the client."""
        self.client = self.client_class()  # Reset the client session
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="StrongPassword123",
            first_name="Test",
            last_name="User"
        )

        # Define login and logout URLs
        self.login_url = reverse("account_login")
        self.logout_url = reverse("account_logout")
        
    def tearDown(self):
        """Ensure session is cleared after each test."""
        self.client.logout()

    def test_login_with_valid_credentials(self):
        """Test that a user can log in with valid email and password."""
        
        # Force login to bypass the authentication process
        self.client.force_login(self.user)

        # Make a request to a page that requires authentication
        response = self.client.get(reverse("home"))  

        # Check that user is authenticated
        self.assertTrue("_auth_user_id" in self.client.session, "User is not authenticated")
        self.assertTrue(response.context["user"].is_authenticated, "User is not authenticated in response context")
        self.assertEqual(response.status_code, 200)

        user = CustomUser.objects.get(email="testuser@example.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_login_with_invalid_email(self):
        """Test login fails with an incorrect email."""
        response = self.client.post(self.login_url, {
            "login": "wrongemail@example.com",
            "password": "StrongPassword123"
        })

        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "The email address and/or password you specified are not correct.", status_code=200)

    def test_login_with_invalid_password(self):
        """Test that login fails when an incorrect password is provided."""

        # Attempt to log in with a valid email but an incorrect password
        response = self.client.post(self.login_url, {
            "login": "testuser@example.com",
            "password": "WrongPassword!"
        })

        # Ensure that the user is not authenticated after the failed login attempt
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Check that the response contains an appropriate error message
        # and that the status code is 200, indicating the form was re-rendered
        self.assertContains(response, "The email address and/or password you specified are not correct.", status_code=200)
        
    def test_login_with_empty_credentials(self):
        """Test login fails when email and password fields are empty."""
        response = self.client.post(self.login_url, {"login": "", "password": ""})

        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "This field is required.", status_code=200)
    
    def test_login_with_missing_password(self):
        """Test login fails when password is not provided."""
        response = self.client.post(self.login_url, {"login": "testuser@example.com", "password": ""})

        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "This field is required.", status_code=200)
        
    def test_login_with_missing_email(self):
        """Test login fails when email is not provided."""
        response = self.client.post(self.login_url, {"login": "", "password": "StrongPassword123"})

        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "This field is required.", status_code=200)
    
    def test_login_with_inactive_user(self):
        """Test that login fails when the user account is inactive."""
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.login_url, {
            "login": "testuser@example.com",
            "password": "StrongPassword123"
        })

        self.assertEqual(response.status_code, 302)  # Ensure it's a redirect
        self.assertTrue(response.url.startswith(reverse("account_inactive")))  # Confirm redirect location

    def test_template_login(self):
        """Tests the template used in the login"""
        response = self.client.post(self.login_url, {
            "login": "testuser@example.com",
            "password": "StrongPassword123"
        }, follow=True)
        self.assertTemplateUsed(response, 'account/login.html') 
            
    def test_user_logout(self):
        """Test user logout."""
        self.client.force_login(self.user)  # Force login
        response = self.client.get(self.logout_url, follow=True) # follow the logout url
    
        self.assertEqual(response.status_code, 200) # success code
        self.assertTemplateUsed(response, 'account/logout.html')  # logout template used



        
    
        

