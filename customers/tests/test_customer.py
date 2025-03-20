from django.test import TestCase, Client
from ..models import *
# Create your tests here.
from django.db import IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from app_users.models import CustomUser
from customers.models import *
# import necessary datetime modules
from datetime import datetime
from datetime import timedelta  
from django.utils import timezone

# import to test image uploads:
from django.core.files.uploadedfile import SimpleUploadedFile  

class CustomerModelTestCase(TestCase):
    """Tests the customers app customer model."""
    def setUp(self):
        self.first_name = "Joe"
        self.last_name = "Smith"
        self.customer_type ="person"
        self.customer_type_business ="business"
        self.customer_type_organization ="organization"
        self.customer_type_government ="government"
        self.customer_type_farm ="farm"
        self.business_name = "Business 1"
        self.farm_name = "Farm 1"
        self.government_name ="Government 1"        
        self.organization_name ="Organization 1"
        self.user1 = CustomUser.objects.create_user(email="user1@test.com", password="testpassword1", first_name="First", last_name="Last")



    def test_can_create_customer_with_required_fields(self):
        """Tests that a customer instance can be successfully created when all required fields are provided."""
        person= Customer.objects.create(first_name=self.first_name, last_name=self.last_name, customer_type=self.customer_type, creator=self.user1)
        self.assertIsNotNone(person, msg="Customer instance should not be none.")
        self.assertEqual(person.first_name, self.first_name, msg="Customer instance first name should match expected first name value.")
        self.assertEqual(person.last_name, self.last_name, msg="Customer instance last name should match expected last name value." )
        self.assertEqual(person.customer_type, self.customer_type, msg="Customer instance customer type should match expected 'person' type.")
        self.assertEqual(person.creator, self.user1, msg="Customer instance creator should match user1 FK profile")

        
    def test_cannot_create_customer_with_missing_required_frist_name(self):
        """Tests that a Validation error is successfully raised when a customer instance is missing a required field: first name"""
        customer = Customer(last_name=self.last_name, customer_type=self.customer_type, creator=self.user1)
        with self.assertRaises(ValidationError) as e:
            customer.full_clean()
        self.assertIn('A Person must have a first name.', str(e.exception))
    
    def test_cannot_create_customer_with_missing_required_last_name(self):
        """Tests that a Validation error is successfully raised when a customer instance is missing a required field: last name"""
        customer = Customer(first_name=self.first_name, customer_type=self.customer_type, creator=self.user1)
        with self.assertRaises(ValidationError) as e:
            customer.full_clean()
        self.assertIn('A Person must have a last name.', str(e.exception))
    
    def test_cannot_create_customer_with_missing_required_creator(self):
        """Tests that a Validation error is successfully raised when a customer instance is missing a required field: creator - FK to CustomUser"""
        customer = Customer(first_name=self.first_name, last_name=self.last_name, customer_type=self.customer_type)
        with self.assertRaises(ValidationError) as e:
            customer.full_clean()
        self.assertIn('creator', str(e.exception))

    def test_cannot_create_non_person_customer_with_last_name(self):
        """Tests that a Validation error is successfully raised when a customer instance of non-person customer types includes field: last_name"""
        non_person_customer_types = [
            (self.customer_type_business, self.business_name),
            (self.customer_type_farm, self.farm_name),
            (self.customer_type_organization, self.organization_name),
            (self.customer_type_government, self.government_name)

        ]

        for customer_type, first_name in non_person_customer_types:
            customer = Customer(first_name=first_name, last_name="Invalid Last Name", customer_type=customer_type, creator=self.user1)
            with self.assertRaises(ValidationError) as e:
                customer.full_clean()
            self.assertIn('For non-person entities, please do not include a last name. Add a First Name, only.', str(e.exception))
    
    def test_can_create_non_person_customer(self):
        """Tests that a customer instances of non-person customer types can be successfully added."""
        non_person_customer_types = [
            (self.customer_type_business, self.business_name),
            (self.customer_type_farm, self.farm_name),
            (self.customer_type_organization, self.organization_name),
            (self.customer_type_government, self.government_name)
        ]

        for customer_type, first_name in non_person_customer_types:
            customer = Customer.objects.create(first_name=first_name, customer_type=customer_type, creator=self.user1)
            self.assertEqual(customer.first_name, first_name, msg="Customer instance first name should match expected first name value.")
            self.assertEqual(customer.last_name, '', msg="Customer instance last name should be empty for non-person customers.")
            self.assertEqual(customer.customer_type, customer_type, msg="Customer instance customer type should match expected non-person type.")
            self.assertEqual(customer.creator, self.user1, msg="Customer instance creator should match expected self.user1 profile")

    def test_cannot_create_customer_with_invalid_customer_type(self):
        """Tests that a Validation error is successfully raised when a customer instance is given an invalid customer type"""
        customer = Customer(first_name=self.first_name, customer_type="invalid type", creator=self.user1)
        with self.assertRaises(ValidationError) as e: # test fails if validation error is not raised
            customer.full_clean()
        self.assertIn("Value 'invalid type' is not a valid choice.", str(e.exception))

    
    def test_cannot_create_customer_with_nonexistent_creator(self):
        """Tests that a Validation error is successfully raised when a customer instance with a user that does not exist is created"""
        customer = Customer(first_name=self.first_name, last_name=self.last_name, customer_type=self.customer_type, creator_id=500)
        with self.assertRaises(ValidationError) as e:
            customer.full_clean()
        self.assertIn("CompanyUser instance with id 500 does not exist.", str(e.exception))

    def test_created_at_datetime_instance(self):
        """Tests that the created_at field is a datetime instance and accurate"""
        person= Customer.objects.create(first_name=self.first_name, last_name=self.last_name, customer_type=self.customer_type, creator=self.user1)
        self.assertIsInstance(person.created_at, datetime, msg="The person created_at field should be an instance of datetime")
        self.assertAlmostEqual(person.created_at, timezone.now(), delta=timedelta(seconds=1), msg="The time that the customer is created should be within 1 second of the current time.")

    def test_customer_is_active_on_creation(self):
        person= Customer.objects.create(first_name=self.first_name, last_name=self.last_name, customer_type=self.customer_type, creator=self.user1)
        self.assertFalse(person.is_inactive)

    def test_first_name_max_length(self):
            """Tests that the first_name field enforces its maximum length of 75 characters."""
            # Create a first name with exactly 75 characters
            valid_first_name = "M" * 75
            customer = Customer.objects.create(
                first_name=valid_first_name,
                last_name="Smith",
                customer_type="person",
                creator=self.user1,
            )
            self.assertEqual(customer.first_name, valid_first_name)

            # Try to create a first name with 76 characters (should raise ValidationError)
            invalid_first_name = "A" * 76
            customer = Customer(first_name=invalid_first_name, last_name="Smith", customer_type="person", creator=self.user1)
            with self.assertRaises(ValidationError):
                customer.full_clean() 

    def test_last_name_max_length(self):
        """Tests that the last_name field enforces its maximum length of 75 characters."""
        # Create a last name with exactly 75 characters
        valid_last_name = "a" * 75
        customer = Customer.objects.create(
            first_name="Joe",
            last_name=valid_last_name,
            customer_type="person",
            creator=self.user1,
        )
        self.assertEqual(customer.last_name, valid_last_name)

        # Try to create a last name with 76 characters (should raise ValidationError)
        invalid_last_name = "A" * 76
        customer = Customer(first_name="Joe", last_name=invalid_last_name, customer_type="person", creator=self.user1)
        with self.assertRaises(ValidationError):
            customer.full_clean()  

    def test_customer_type_max_length(self):
        """Tests that the customer_type field enforces its maximum length of 12 characters."""
        # Create a customer with a valid customer_type
        valid_customer_type = "person"  # Length is 6
        customer = Customer.objects.create(
            first_name="Joe",
            last_name="Smith",
            customer_type=valid_customer_type,
            creator=self.user1,
        )
        self.assertEqual(customer.customer_type, valid_customer_type)

        # Try to create a customer with an invalid customer_type (length > 12)
        invalid_customer_type = "A" * 13  # Length is 13
        customer = Customer(first_name="Joe", last_name="Smith", customer_type=invalid_customer_type, creator=self.user1)
        with self.assertRaises(ValidationError):
            customer.full_clean()  
            
    def test_clean_method_for_person(self):
        """Tests the clean method for a customer of type 'person'."""
        # Valid case: Both first_name and last_name are provided
        customer = Customer(
            first_name="Joe",
            last_name="Smith",
            customer_type="person",
            creator=self.user1,
        )
        customer.full_clean()  # Should not raise an error

        # Invalid case: Missing first_name
        customer = Customer(
            first_name="",
            last_name="Smith",
            customer_type="person",
            creator=self.user1,
        )
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        self.assertIn("A Person must have a first name.", str(context.exception))

        # Invalid case: Missing last_name
        customer = Customer(
            first_name="Joe",
            last_name="",
            customer_type="person",
            creator=self.user1,
        )
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        self.assertIn("A Person must have a last name.", str(context.exception))

    def test_clean_method_for_non_person(self):
        """Tests the clean method for non-person customers."""
        # Valid case: Only first_name is provided
        customer = Customer(
            first_name="Business 1",
            last_name="",
            customer_type="business",
            creator=self.user1,
        )
        customer.full_clean()  # Should not raise an error

        # Invalid case: last_name is provided for a non-person customer
        customer = Customer(
            first_name="Business 1",
            last_name="Invalid Last Name",
            customer_type="business",
            creator=self.user1,
        )
        with self.assertRaises(ValidationError) as context:
            customer.full_clean()
        self.assertIn("For non-person entities, please do not include a last name. Add a First Name, only.", str(context.exception))

    def test_str_method_for_person(self):
        """Tests the __str__ method for a customer of type 'person'."""
        customer = Customer(
            first_name="Joe",
            last_name="Smith",
            customer_type="person",
            creator=self.user1,
        )
        self.assertEqual(str(customer), "Joe Smith")

    def test_str_method_for_non_person(self):
        """Tests the __str__ method for non-person customers."""
        customer = Customer(
            first_name="Business 1",
            last_name="",
            customer_type="business",
            creator=self.user1,
        )
        self.assertEqual(str(customer), "Business 1 (Business)")

class PreferredContactMethodsTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create_user(email="user@test.com", password="testpassword")

        # Create a customer
        self.customer = Customer.objects.create(
            first_name="Joe",
            last_name="Smith",
            customer_type="person",
            creator=self.user,
        )

        # Create contact methods
        self.contact_method_email = ContactMethod.objects.create(method_name="email")
        self.contact_method_phone = ContactMethod.objects.create(method_name="phone")

    def test_add_preferred_contact_methods(self):
        """Tests that multiple preferred contact methods can be added to a Customer instance."""
        # Add preferred contact methods
        self.customer.preferred_contact_methods.add(self.contact_method_email, self.contact_method_phone)

        # Verify the preferred contact methods
        self.assertEqual(self.customer.preferred_contact_methods.first(), self.contact_method_email, msg="Email should be the first preferred contact method")
        self.assertIn(self.contact_method_email, self.customer.preferred_contact_methods.all(), msg="Email should be a preferred contact method")
        self.assertIn(self.contact_method_phone, self.customer.preferred_contact_methods.all(), msg="Phone should be a preferred contact method")
        self.assertEqual(self.customer.preferred_contact_methods.count(), 2, msg="There should be two preferred contact methods")

    def test_remove_preferred_contact_method(self):
        """Tests that a contact method can be removed from the preferred contact methods."""
        # Add preferred contact methods
        self.customer.preferred_contact_methods.add(self.contact_method_email, self.contact_method_phone)

        # Remove one contact method
        self.customer.preferred_contact_methods.remove(self.contact_method_email)

        # Verify the remaining contact methods
        self.assertNotIn(self.contact_method_email, self.customer.preferred_contact_methods.all(), msg="Email should not be a preferred contact method after removal")
        self.assertEqual(self.customer.preferred_contact_methods.count(), 1, msg="There should be 1 preferred contact method after removal")

    def test_clear_preferred_contact_methods(self):
        """Tests that all contact methods can be cleared from the preferred contact methods."""
        # Add preferred contact methods
        self.customer.preferred_contact_methods.add(self.contact_method_email, self.contact_method_phone)

        # Clear all contact methods
        self.customer.preferred_contact_methods.clear()

        # Verify that no contact methods remain
        self.assertEqual(self.customer.preferred_contact_methods.count(), 0, msg="There should be no preferred contact methods after clearing")

    def test_add_duplicate_preferred_contact_method(self):
        """Tests that a duplicate contact method cannot be added to the preferred contact methods."""
        # Add a contact method
        self.customer.preferred_contact_methods.add(self.contact_method_email)

        # Attempt to add the same contact method again
        self.customer.preferred_contact_methods.add(self.contact_method_email)

        # Verify that only one instance of the contact method exists
        self.assertEqual(self.customer.preferred_contact_methods.count(), 1, msg="There should only be one preferred contact method after adding an email twice")

    def test_preferred_contact_methods_display(self):
        """Tests the preferred_contact_methods_display property."""
        # Test when no preferred contact methods are added
        self.assertEqual(self.customer.preferred_contact_methods_display, "No preferred contact method.", msg="If no contact methods have been added, there should be none displayed")

        # Add preferred contact methods
        self.customer.preferred_contact_methods.add(self.contact_method_email, self.contact_method_phone)

        # Test when preferred contact methods are added
        self.assertEqual(self.customer.preferred_contact_methods_display, "email, phone", msg="Added contact methods should show as a string") 

class CustomerPropertiesTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create_user(email="user@test.com", password="testpassword")

        # Create a customer
        self.customer = Customer.objects.create(
            first_name="Joe",
            last_name="Smith",
            customer_type="person",
            creator=self.user,
        )

        # Create related objects for testing
        self.contact_method_email = ContactMethod.objects.create(method_name="email")
        self.contact_method_phone = ContactMethod.objects.create(method_name="phone")

        self.phone = Phone.objects.create(
            phone_number="330-674-2811",
            phone_type="CELL",
            is_primary=True,

        )

        self.email = Email.objects.create(
            email_address="test@example.com",
            email_type="HOME",
            preferred_email=True,
        )

        self.address = Address.objects.create(
            street="123 Main St",
            city="City",
            state="OH",
            zip_code="12345",
            mailing_address=True,
        )

    def test_display_name_property(self):
        """Tests the display_name property of the Customer model."""
        # tests if the display name is as expected for a person
        self.assertEqual(self.customer.display_name, "Joe Smith")

        # Test for a non-person customer
        business_customer = Customer.objects.create(
            first_name="Business 1",
            customer_type="business",
            creator=self.user,
        )
        self.assertEqual(business_customer.display_name, "Business 1 (business)")

    def test_preferred_contact_methods_display_property(self):
        """Tests the preferred_contact_methods_display property."""
        # Test when no preferred contact methods are added
        self.assertEqual(self.customer.preferred_contact_methods_display, "No preferred contact method.")

        # Add preferred contact methods
        self.customer.preferred_contact_methods.add(self.contact_method_email, self.contact_method_phone)

        # Test when preferred contact methods are added
        self.assertEqual(self.customer.preferred_contact_methods_display, "email, phone")

    def test_has_primary_phone_property(self):
        """Tests the has_primary_phone property."""
        # Test when a primary phone exists by first adding it to the customer instance
        self.customer.phones.add(self.phone)
        self.assertTrue(self.customer.has_primary_phone)

        # set the primary_phone field to False
        self.phone.is_primary = False
        self.phone.save()  # save change to db
        self.assertFalse(self.customer.has_primary_phone)

    def test_primary_phone_details_property(self):
        """Tests the primary_phone_details property."""
        self.customer.phones.add(self.phone) # add the phone number to the customer instance

        # Test when a primary phone exists
        expected_output = "330-674-2811 (CELL) - (1 phone number)"
        self.assertEqual(self.customer.primary_phone_details, expected_output)

        # Remove the primary phone
        self.phone.is_primary = False
        self.phone.save()

        # Test when no primary phone exists
        self.assertEqual(self.customer.primary_phone_details, "No primary phone number.")

    def test_preferred_email_property(self):
        """Tests the preferred_email property."""
        self.customer.emails.add(self.email) # add the email to the customer instance

        # Test when a preferred email exists
        expected_output = "test@example.com (HOME)"
        self.assertEqual(self.customer.preferred_email, expected_output)

        # Remove the preferred email
        self.email.preferred_email = False
        self.email.save()

        # Test when no preferred email exists
        self.assertEqual(self.customer.preferred_email, "No preferred email.")

    def test_email_count_property(self):
        """Tests the email_count property."""
        
        self.customer.emails.add(self.email) # add the email to the customer instance

        # Test when emails exist
        self.assertEqual(self.customer.email_count, "1 email")

        # Add another email
        email2 = Email.objects.create(
            email_address="test2@example.com",
            email_type="WORK",
        )
        self.customer.emails.add(email2) # add the 2nd email to the customer instance


        # Test when multiple emails exist
        self.assertEqual(self.customer.email_count, "2 emails")

    def test_mailing_address_property(self):
        """Tests the mailing_address property."""
        # Test when a mailing address exists
        expected_output = "123 Main St City, OH 12345"
        self.customer.addresses.add(self.address) # add the address to the customer instance

        self.assertEqual(self.customer.mailing_address, expected_output)

        # Remove the mailing address
        self.address.mailing_address = False
        self.address.save()

        # Test when no mailing address exists
        self.assertEqual(self.customer.mailing_address, "No mailing address.")

    def test_address_count_property(self):
        """Tests the address_count property."""
        # Test when addresses exist
        self.customer.addresses.add(self.address) # add the address to the customer instance

        self.assertEqual(self.customer.address_count, "1 address")

        # Add another address
        address2=Address.objects.create(
            street="456 West St",
            city="Town",
            state="MI",
            zip_code="67899",
        )
        self.customer.addresses.add(address2) # add the 2nd address to the customer instance

        # Test when multiple addresses exist
        self.assertEqual(self.customer.address_count, "2 addresses")

    def test_phone_count_property(self):
        """Tests the phone_count property."""
        # Test when phones exist
        self.customer.phones.add(self.phone) # add the phone to the customer instance

        self.assertEqual(self.customer.phone_count, "1 phone number")

        # Add another phone
        phone2=Phone.objects.create(
            phone_number="330-674-2812",
            phone_type="HOME",
        )
        self.customer.phones.add(phone2) # add 2nd phone to the customer instance


        # Test when multiple phones exist
        self.assertEqual(self.customer.phone_count, "2 phone numbers")



class CustomerManyToManyRelationshipsTest(TestCase):
    def setUp(self):
        # Create a user for the creator field
        self.user = CustomUser.objects.create_user(email="user@test.com", password="testpassword")

        # Create a customer
        self.customer = Customer.objects.create(
            first_name="Joe",
            last_name="Smith",
            customer_type="person",
            creator=self.user,
        )

        # Create related objects for testing
        self.interest1 = CustomerInterest.objects.create(name="Interest 1", slug="interest-1")
        self.interest2 = CustomerInterest.objects.create(name="Interest 2", slug="interest-2")

        self.address1 = Address.objects.create(
            street="123 Main St",
            city="City",
            state="ST",
            zip_code="12345",
        )
        self.address2 = Address.objects.create(
            street="456 Elm St",
            city="Town",
            state="ST",
            zip_code="67890",
        )

        self.phone1 = Phone.objects.create(
            phone_number="330-674-2811",
            phone_type="CELL",
        )
        self.phone2 = Phone.objects.create(
            phone_number="330-674-2812",
            phone_type="HOME",
        )

        self.email1 = Email.objects.create(
            email_address="test1@example.com",
            email_type="HOME",
        )
        self.email2 = Email.objects.create(
            email_address="test2@example.com",
            email_type="WORK",
        )

    def test_interests_relationship(self):
        """Tests the many-to-many relationship between Customer and CustomerInterest."""
        # Add interests to the customer
        self.customer.interests.add(self.interest1, self.interest2)

        # Verify the interests were added
        self.assertIn(self.interest1, self.customer.interests.all())
        self.assertIn(self.interest2, self.customer.interests.all())
        self.assertEqual(self.customer.interests.count(), 2)
        
        # Remove an interest
        self.customer.interests.remove(self.interest1)
        self.assertNotIn(self.interest1, self.customer.interests.all())
        self.assertEqual(self.customer.interests.count(), 1)

        # Clear all interests
        self.customer.interests.clear()
        self.assertEqual(self.customer.interests.count(), 0)


    def test_addresses_relationship(self):
        """Tests the many-to-many relationship between Customer and Address."""
        # Add addresses to the customer
        self.customer.addresses.add(self.address1, self.address2)

        # Verify the addresses were added
        self.assertIn(self.address1, self.customer.addresses.all())
        self.assertIn(self.address2, self.customer.addresses.all())
        self.assertEqual(self.customer.addresses.count(), 2)

        # Remove an address
        self.customer.addresses.remove(self.address1)
        self.assertNotIn(self.address1, self.customer.addresses.all())
        self.assertEqual(self.customer.addresses.count(), 1)

        # Clear all addresses
        self.customer.addresses.clear()
        self.assertEqual(self.customer.addresses.count(), 0)

    def test_phones_relationship(self):
        """Tests the many-to-many relationship between Customer and Phone."""
        # Add phones to the customer
        self.customer.phones.add(self.phone1, self.phone2)

        # Verify the phones were added
        self.assertIn(self.phone1, self.customer.phones.all())
        self.assertIn(self.phone2, self.customer.phones.all())
        self.assertEqual(self.customer.phones.count(), 2)

        # Remove a phone
        self.customer.phones.remove(self.phone1)
        self.assertNotIn(self.phone1, self.customer.phones.all())
        self.assertEqual(self.customer.phones.count(), 1)

        # Clear all phones
        self.customer.phones.clear()
        self.assertEqual(self.customer.phones.count(), 0)

    def test_emails_relationship(self):
        """Tests the many-to-many relationship between Customer and Email."""
        # Add emails to the customer
        self.customer.emails.add(self.email1, self.email2)

        # Verify the emails were added
        self.assertIn(self.email1, self.customer.emails.all())
        self.assertIn(self.email2, self.customer.emails.all())
        self.assertEqual(self.customer.emails.count(), 2)

        # Remove an email
        self.customer.emails.remove(self.email1)
        self.assertNotIn(self.email1, self.customer.emails.all())
        self.assertEqual(self.customer.emails.count(), 1)

        # Clear all emails
        self.customer.emails.clear()
        self.assertEqual(self.customer.emails.count(), 0)

    def test_duplicate_entries(self):
        """Tests that duplicate entries are not allowed in many-to-many relationships."""
        # Add the same interest twice
        self.customer.interests.add(self.interest1)
        self.customer.interests.add(self.interest1)
        self.assertEqual(self.customer.interests.count(), 1)

        # Add the same address twice
        self.customer.addresses.add(self.address1)
        self.customer.addresses.add(self.address1)
        self.assertEqual(self.customer.addresses.count(), 1)

        # Add the same phone twice
        self.customer.phones.add(self.phone1)
        self.customer.phones.add(self.phone1)
        self.assertEqual(self.customer.phones.count(), 1)

        # Add the same email twice
        self.customer.emails.add(self.email1)
        self.customer.emails.add(self.email1)
        self.assertEqual(self.customer.emails.count(), 1)
    def setUp(self):
        """
        Set up test data for the Customer model.
        """
        # Create a CustomUser for the creator field
        self.user = CustomUser.objects.create(email="test@email.com", password="password123")

        # Create a Customer instance
        self.customer_person = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            customer_type="person",
            creator=self.user,
        )

        self.customer_business = Customer.objects.create(
            first_name="Acme Corp",
            customer_type="business",
            creator=self.user,
        )

        # Create related objects for ManyToMany fields
        self.contact_method = ContactMethod.objects.create(method_name="Email")
        self.name = CustomerInterest.objects.create(name="Gardening")
        self.address = Address.objects.create(
            street="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
            mailing_address=True,
        )
        self.phone = Phone.objects.create(
            phone_number="555-1234",
            phone_type="Mobile",
            is_primary=True,
        )
        self.email = Email.objects.create(
            email_address="john.doe@example.com",
            email_type="Personal",
            preferred_email=True,
        )

        # Add related objects to the customer
        self.customer_person.preferred_contact_methods.add(self.contact_method)
        self.customer_person.interests.add(self.name)
        self.customer_person.addresses.add(self.address)
        self.customer_person.phones.add(self.phone)
        self.customer_person.emails.add(self.email)

    def test_customer_creation(self):
        """
        Test that a Customer instance is created correctly.
        """
        self.assertEqual(self.customer_person.first_name, "John")
        self.assertEqual(self.customer_person.last_name, "Doe")
        self.assertEqual(self.customer_person.customer_type, "person")
        self.assertEqual(self.customer_person.creator, self.user)

    def test_customer_str_method(self):
        """
        Test the __str__ method of the Customer model.
        """
        self.assertEqual(str(self.customer_person), "John Doe")
        self.assertEqual(str(self.customer_business), "Acme Corp (Business)")

    def test_customer_clean_method_person(self):
        """
        Test the clean method for a customer of type "person".
        """
        # Valid case: Both first_name and last_name are provided
        customer = Customer(
            first_name="Jane",
            last_name="Smith",
            customer_type="person",
            creator=self.user,
        )
        customer.clean()  # Should not raise an error

        # Invalid case: Missing first_name
        customer.first_name = ""
        with self.assertRaises(ValidationError):
            customer.clean()

        # Invalid case: Missing last_name
        customer.first_name = "Jane"
        customer.last_name = ""
        with self.assertRaises(ValidationError):
            customer.clean()

    def test_customer_clean_method_non_person(self):
        """
        Test the clean method for a customer of type other than "person".
        """
        # Valid case: Only first_name is provided
        customer = Customer(
            first_name="Acme Corp",
            customer_type="business",
            creator=self.user,
        )
        customer.clean()  # Should not raise an error

        # Invalid case: last_name is provided for a non-person entity
        customer.last_name = "Corp"
        with self.assertRaises(ValidationError):
            customer.clean()

    def test_display_name_property(self):
        """
        Test the display_name property.
        """
        self.assertEqual(self.customer_person.display_name, "John Doe")
        self.assertEqual(self.customer_business.display_name, "Acme Corp (business)")

    def test_preferred_contact_methods_display_property(self):
        """
        Test the preferred_contact_methods_display property.
        """
        self.assertEqual(
            self.customer_person.preferred_contact_methods_display,
            "Email",
        )

    def test_count_notes_property(self):
        """
        Test the count_notes property.
        """
        self.assertEqual(self.customer_person.count_notes, "No notes.")

    def test_count_documents_property(self):
        """
        Test the count_documents property.
        """
        self.assertEqual(self.customer_person.count_documents, "No documents.")

    def test_has_primary_phone_property(self):
        """
        Test the has_primary_phone property.
        """
        self.assertTrue(self.customer_person.has_primary_phone)

    def test_primary_phone_details_property(self):
        """
        Test the primary_phone_details property.
        """
        self.assertEqual(
            self.customer_person.primary_phone_details,
            "555-1234 (Mobile) - (1 phone number)",
        )

    def test_preferred_email_property(self):
        """
        Test the preferred_email property.
        """
        self.assertEqual(
            self.customer_person.preferred_email,
            "john.doe@example.com (Personal)",
        )

    def test_email_count_property(self):
        """
        Test the email_count property.
        """
        self.assertEqual(self.customer_person.email_count, "1 email")

    def test_mailing_address_property(self):
        """
        Test the mailing_address property.
        """
        self.assertEqual(
            self.customer_person.mailing_address,
            "123 Main St Springfield, IL 62701",
        )

    def test_address_count_property(self):
        """
        Test the address_count property.
        """
        self.assertEqual(self.customer_person.address_count, "1 address")

    def test_phone_count_property(self):
        """
        Test the phone_count property.
        """
        self.assertEqual(self.customer_person.phone_count, "1 phone number")