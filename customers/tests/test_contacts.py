from django.test import TestCase
from django.core.exceptions import ValidationError
from customers.models import Address, Email, Phone, ContactMethod
from django.db import IntegrityError

class AddressModelTestCase(TestCase):
    def setUp(self):
        """
            Sets up test data for the Address model.
        """
        self.address = Address.objects.create(
            street="123 Ridge Rd",
            city="Albany",
            state="IL",
            zip_code="89561",
            mailing_address=True,
        )

    def test_address_creation(self):
        """
            Tests that an Address instance is created correctly.
        """
        self.assertEqual(self.address.street, "123 Ridge Rd")
        self.assertEqual(self.address.city, "Albany")
        self.assertEqual(self.address.state, "IL")
        self.assertEqual(self.address.zip_code, "89561")
        self.assertTrue(self.address.mailing_address)
        
    def test_street_blank(self):
        """
            Tests that the street field can be blank if not a mailing address
        """
        address = Address(
            city="Gambier",
            state="IL",
            zip_code="12345",
            street="",  # Blank street
            mailing_address=False,

        )
        address.full_clean()  
        address.save()
        self.assertEqual(address.street, "", "The street field should allow blank values.")

    def test_street_null(self):
        """
            Tests that the street field can be NULL if not a mailing address
        """
        address = Address(
            city="Gambier",
            state="IL",
            zip_code="12345",
            street=None,  # NULL street
            mailing_address=False,

        )
        address.full_clean() 
        address.save()
        self.assertIsNone(address.street, "The street field should allow NULL values.")
        
    def test_street_blank_for_mailing_address(self):
        """
        Tests that the street field cannot be blank for a mailing address.
        """
        address = Address(
            city="Gambier",
            state="IL",
            zip_code="12345",
            street="",  # Blank street
            mailing_address=True,  # This is a mailing address
        )
        with self.assertRaises(ValidationError, msg="The street field should raise a ValidationError for blank values in mailing addresses."):
            address.full_clean()  # Should raise a ValidationError
    
    def test_street_null_for_mailing_address(self):
        """
        Tests that the street field cannot be NULL for a mailing address.
        """
        address = Address(
            city="Gambier",
            state="IL",
            zip_code="12345",
            street=None,  # Blank street
            mailing_address=True,  # This is a mailing address
        )
        with self.assertRaises(ValidationError, msg="The street field should raise a ValidationError for blank values in mailing addresses."):
            address.full_clean()  

    def test_street_max_length(self):
        """
        Tests that the street field enforces the maximum length of 255 characters.
        """
        # Create a street value with 255 characters (valid)
        valid_street = "a" * 255
        address = Address(
            city="Gambier",
            state="IL",
            zip_code="12345",
            street=valid_street,
        )
        address.full_clean()  # Should not raise an error
        address.save()
        self.assertEqual(address.street, valid_street, "The street field should allow 255 characters.")

        # Create a street value with 256 characters (invalid)
        invalid_street = "a" * 256
        address.street = invalid_street
        with self.assertRaises(ValidationError, msg="The street field should raise a ValidationError for values longer than 255 characters."):
            address.full_clean()
            
    def test_city_blank(self):
        """
        Tests that the city field cannot be blank.
        """
        address = Address(
            street="123 Main St",
            state="IL",
            zip_code="12345",
            city="",  # Blank city
        )
        with self.assertRaises(ValidationError, msg="The city field should raise a ValidationError for blank values."):
            address.full_clean()  # Should raise a ValidationError

    def test_city_null(self):
        """
        Tests that the city field cannot be NULL.
        """
        address = Address(
            street="123 Main St",
            state="IL",
            zip_code="12345",
            city=None,  # NULL city
        )
        with self.assertRaises(ValidationError, msg="The city field should raise a ValidationError for NULL values."):
            address.full_clean()  # Should raise a ValidationError

    def test_city_max_length(self):
        """
        Tests that the city field enforces the maximum length of 100 characters.
        """
        # Create a city value with 100 characters (valid)
        valid_city = "a" * 100
        address = Address(
            street="123 Main St",
            state="IL",
            zip_code="12345",
            city=valid_city,
        )
        address.full_clean()  # Should not raise an error
        address.save()
        self.assertEqual(address.city, valid_city, "The city field should allow 100 characters.")

        # Create a city value with 101 characters (invalid)
        invalid_city = "a" * 101
        address.city = invalid_city
        with self.assertRaises(ValidationError, msg="The city field should raise a ValidationError for values longer than 100 characters."):
            address.full_clean()  # Should raise a ValidationError

    def test_address_str_method(self):
        """
            Tests the __str__ method of the Address model.
        """
        self.assertEqual(str(self.address), "Mailing Address: 123 Ridge Rd, Albany, IL 89561")
        
    def test_invalid_state_choice(self):
        """
        Tests that an invalid state choice raises a ValidationError.
        """
        # Attempt to create an Address instance with an invalid state 'XY
        invalid_state = "XY"  # This is not a valid choice in STATE_CHOICES
        address = Address(
            city="Wooster",
            state=invalid_state,  
            zip_code="12345",
        )

        # a validation error should be raised for an invalid state choice
        with self.assertRaises(ValidationError, msg="An invalid state choice should raise a ValidationError."):
            address.full_clean()  
            
    def test_state_null(self):
        """
        Tests that the state field cannot be NULL.
        """
        address = Address(
            street="123 Main St",
            city="Springfield",
            zip_code="12345",
            state=None,  # NULL state
        )
        with self.assertRaises(ValidationError, msg="The state field should raise a ValidationError for NULL values."):
            address.full_clean()  # Should raise a ValidationError

    def test_address_clean_method_valid(self):
        """
            Tests the clean method for a valid Address instance.
        """
        address = Address(
            street="456 Elm St",
            city="Albany",
            state="IL",
            zip_code="89561",
            mailing_address=True,
        )
        address.clean()  
        
    def test_address_clean_method_invalid(self):
        """
            Tests the clean method for an invalid Address instance (missing street for mailing address).
        """
        address = Address(
            street="",
            city="Albany",
            state="IL",
            zip_code="89561",
            mailing_address=True,
        )
        with self.assertRaises(ValidationError):
            address.clean()

    def test_address_clean_method_non_mailing(self):
        """
        Test the clean method for a non-mailing address (street not required).
        """
        address = Address(
            street="",
            city="Albany",
            state="IL",
            zip_code="89561",
            mailing_address=False,
        )
        address.clean()  # Should not raise an error
    def test_zip_code_valid(self):
                """
                Tests that the zip_code field accepts valid 5-digit values.
                """
                valid_zip_code = "90001"  # A valid 5-digit zip code for Los Angeles, CA
                address = Address(
                    street="123 Sunset Blvd",
                    city="Los Angeles",
                    state="CA",
                    zip_code=valid_zip_code,
                )
                address.full_clean()  # Should not raise an error
                address.save()
                self.assertEqual(address.zip_code, valid_zip_code, "The zip_code field should accept valid 5-digit values.")

    def test_zip_code_too_short(self):
        """
        Tests that the zip_code field raises a ValidationError for values shorter than 5 digits.
        """
        invalid_zip_code = "9001"  # 4 digits (too short)
        address = Address(
            street="123 Sunset Blvd",
            city="Los Angeles",
            state="CA",
            zip_code=invalid_zip_code,
        )
        with self.assertRaises(ValidationError, msg="The zip_code field should raise a ValidationError for values shorter than 5 digits."):
            address.full_clean()  # Should raise a ValidationError

    def test_zip_code_too_long(self):
        """
        Tests that the zip_code field raises a ValidationError for values longer than 5 digits.
        """
        invalid_zip_code = "900012"  # 6 digits (too long)
        address = Address(
            street="123 Sunset Blvd",
            city="Los Angeles",
            state="CA",
            zip_code=invalid_zip_code,
        )
        with self.assertRaises(ValidationError, msg="The zip_code field should raise a ValidationError for values longer than 5 digits."):
            address.full_clean()  # Should raise a ValidationError

    def test_zip_code_non_numeric(self):
        """
        Tests that the zip_code field raises a ValidationError for non-numeric values.
        """
        invalid_zip_code = "9000A"  # Contains a non-numeric character
        address = Address(
            street="123 Sunset Blvd",
            city="Los Angeles",
            state="CA",
            zip_code=invalid_zip_code,
        )
        with self.assertRaises(ValidationError, msg="The zip_code field should raise a ValidationError for non-numeric values."):
            address.full_clean()  # Should raise a ValidationError

    def test_zip_code_blank(self):
        """
        Tests that the zip_code field cannot be blank.
        """
        address = Address(
            street="123 Sunset Blvd",
            city="Los Angeles",
            state="CA",
            zip_code="",  # Blank zip code
        )
        with self.assertRaises(ValidationError, msg="The zip_code field should raise a ValidationError for blank values."):
            address.full_clean()  # Should raise a ValidationError

    def test_zip_code_null(self):
        """
        Tests that the zip_code field cannot be NULL.
        """
        address = Address(
            street="123 Sunset Blvd",
            city="Los Angeles",
            state="CA",
            zip_code=None,  # NULL zip code
        )
        with self.assertRaises(ValidationError, msg="The zip_code field should raise a ValidationError for NULL values."):
            address.full_clean()  # Should raise a ValidationError
            
    def test_mailing_address_default(self):
        """
        Tests that the mailing_address field defaults to True if no value is provided.
        """
        address = Address(
            street="456 Hollywood Blvd",
            city="Los Angeles",
            state="CA",
            zip_code="90028",
        )
        address.full_clean()  # Should not raise an error
        address.save()
        self.assertTrue(address.mailing_address, "The mailing_address field should default to True.")

    def test_mailing_address_set_to_false(self):
        """
        Tests that the mailing_address field can be set to False.
        """
        address = Address(
            street="456 Hollywood Blvd",
            city="Los Angeles",
            state="CA",
            zip_code="90028",
            mailing_address=False,  # Explicitly set to False
        )
        address.full_clean()  # Should not raise an error
        address.save()
        self.assertFalse(address.mailing_address, "The mailing_address field should allow False.")

    def test_mailing_address_set_to_true(self):
        """
        Tests that the mailing_address field can be set to True explicitly.
        """
        address = Address(
            street="456 Hollywood Blvd",
            city="Los Angeles",
            state="CA",
            zip_code="90028",
            mailing_address=True,  # Explicitly set to True
        )
        address.full_clean()  # Should not raise an error
        address.save()
        self.assertTrue(address.mailing_address, "The mailing_address field should allow True.")

    def test_mailing_address_blank(self):
        """
        Tests that the mailing_address field cannot be blank.
        """
        address = Address(
            street="456 Hollywood Blvd",
            city="Los Angeles",
            state="CA",
            zip_code="90028",
            mailing_address="",  # Blank value (invalid for BooleanField)
        )
        with self.assertRaises(ValidationError, msg="The mailing_address field should raise a ValidationError for blank values."):
            address.full_clean()  # Should raise a ValidationError

    def test_mailing_address_null(self):
        """
        Tests that the mailing_address field cannot be NULL.
        """
        address = Address(
            street="456 Hollywood Blvd",
            city="Los Angeles",
            state="CA",
            zip_code="90028",
            mailing_address=None,  # NULL value (invalid for BooleanField)
        )
        with self.assertRaises(ValidationError, msg="The mailing_address field should raise a ValidationError for NULL values."):
            address.full_clean()  # Should raise a ValidationError

class EmailModelTestCase(TestCase):
    def setUp(self):
        """
         Sets up test data for the Email model.
        """
        self.email = Email.objects.create(
            email_address="test@test.com",
            email_type="HOME",
            preferred_email=True,
        )

    def test_email_creation(self):
        """
            Tests that an Email instance is created correctly in the setup method.
        """
        self.assertEqual(self.email.email_address, "test@test.com")
        self.assertEqual(self.email.email_type, "HOME")
        self.assertTrue(self.email.preferred_email)
    
    def test_email_address_is_required(self):
        """Tests that creating a Email instance without an email_address raises an error"""
        # 
        with self.assertRaises(Exception):
            Email.objects.create(email_address=None)

        with self.assertRaises(Exception):
            Email.objects.create(email_address='')

    def test_valid_email_address(self):
        """Tests that a valid email address can be saved in a new email instance"""
        valid_email = "test@test.com"
        email_instance = Email.objects.create(email_address=valid_email)
        self.assertEqual(email_instance.email_address, valid_email)
    
    def test_email_type_valid_choices(self):
        """Tests that valid email type choices are accepted in the creation of a new email instance"""
        valid_choices = ["HOME", "WORK", "FARM"]
        for choice in valid_choices:
            email = Email.objects.create(email_address="test@test.com", email_type=choice)
            self.assertEqual(email.email_type, choice)

    def test_email_type_blank_and_null(self):
        """Tests that the email_type field is not required and can be blank or null"""
        email_blank = Email.objects.create(email_address="test@test.com", email_type="")
        self.assertEqual(email_blank.email_type, "")

        email_null = Email.objects.create(email_address="test@test.com", email_type=None)
        self.assertIsNone(email_null.email_type)

    def test_email_type_invalid_choice(self):
        """Tests that entering an invalid email_type leads to a ValidationError"""
        email = Email(email_address="test@test.com", email_type="INVALID")
        with self.assertRaises(ValidationError):
            email.full_clean()  

    def test_email_str_method(self):
        """
        Tests the __str__ method of the Email model.
        """
        self.assertEqual(str(self.email), "test@test.com (HOME)")

    def test_email_str_method_no_type(self):
        """
        Tests the __str__ method of the Email model when email_type is not provided.
        """
        email = Email.objects.create(
            email_address="test2@test.com",
            email_type="",
            preferred_email=False,
        )
        self.assertEqual(str(email), "test2@test.com")
    
    def test_preferred_email_default_value(self):
        """Tests that the default value for preferred_email is True"""
        email = Email.objects.create(email_address="test@test.com")
        self.assertTrue(email.preferred_email)

    def test_preferred_email_can_be_set_to_false(self):
        """Tests that the preferred_email field can be set to False"""
        email = Email.objects.create(email_address="test@test.com", preferred_email=False)
        self.assertFalse(email.preferred_email)

    def test_preferred_email_can_be_set_to_true(self):
        """Tests that the preferred_email field can be set to True"""
        email = Email.objects.create(email_address="test@test.com", preferred_email=True)
        self.assertTrue(email.preferred_email)

    def test_preferred_email_saved_and_retrieved_correctly(self):
        """Tests that the preferred_email is correctly saved and then retrieved from the db"""
        email = Email.objects.create(email_address="test@test.com", preferred_email=False)
        retrieved_email = Email.objects.get(id=email.id)
        self.assertFalse(retrieved_email.preferred_email)

class PhoneModelTestCase(TestCase):
    def setUp(self):
        """
            Set up test data for the Phone model.
        """
        self.phone = Phone.objects.create(
            phone_number="555-1234",
            phone_type="cell",
            is_primary=True,
        )

    def test_phone_creation(self):
        """
        Test that a Phone instance crated in setUp is created correctly.
        """
        self.assertEqual(self.phone.phone_number, "555-1234")
        self.assertEqual(self.phone.phone_type, "cell")
        self.assertTrue(self.phone.is_primary)

    def test_phone_str_method(self):
        """
        Test the __str__ method of the Phone model.
        """
        self.assertEqual(str(self.phone), "555-1234 (CELL)")

    def test_phone_str_method_with_extension(self):
        """
        Test the __str__ method of the Phone model with an extension.
        """
        phone = Phone.objects.create(
            phone_number="555-5678",
            phone_type="work",
            extension="123",
            is_primary=False,
        )
        self.assertEqual(str(phone), "555-5678 ext:123 (WORK)")

    def test_phone_save_method(self):
        """
        Test the save method of the Phone model to make sure the phone number is formatted correctly.
        """
        phone = Phone(
            phone_number="3306742811",
            phone_type="home",
            is_primary=False,
        )
        phone.save()
        self.assertEqual(phone.phone_number, "330-674-2811")
        
    def test_phone_number_is_required(self):
        """Test tht the phone_number field is required (cannot be null or blank)"""
        with self.assertRaises(Exception):
            Phone.objects.create(phone_number=None)

        with self.assertRaises(Exception):
            Phone.objects.create(phone_number="")

    def test_phone_number_valid_formats(self):
        """Tests that the phone number is reformatted correctly as specified in the save method."""
        # Test that valid phone number formats are reformatted correctly
        test_cases = [
            ("3306742811", "330-674-2811"),  # Input without dashes -> Output with dashes
            ("330-674-2811", "330-674-2811"),  # Input with dashes -> Output is the same
        ]
        
        # iterate over test numbers to make sure the output is as expected
        for input_number, expected_output in test_cases:
            phone = Phone.objects.create(phone_number=input_number)
            self.assertEqual(phone.phone_number, expected_output)

    def test_phone_number_invalid_formats(self):
        """Tests that invalid formats for inputs of the phone_number field raise a ValidationError"""
        invalid_numbers = [
            "330674281",  
            "330-674-281",  
            "abc1234567",  
            "123456789012345",  
            "330-674-2811a",  
        ]
        # iterate over invalid numbers - catch validation errors
        for number in invalid_numbers:
            phone = Phone(phone_number=number)
            with self.assertRaises(ValidationError):
                phone.full_clean()  
                
    def test_extension_optional(self):
        """Tests that extensions can be blank/null"""
        phone_blank = Phone.objects.create(phone_number="3306742811", extension="")
        self.assertEqual(phone_blank.extension, "")

        phone_null = Phone.objects.create(phone_number="3306742811", extension=None)
        self.assertIsNone(phone_null.extension)

    def test_extension_valid_formats(self):
        """Tests valid extension formats, including an empty string"""
        valid_extensions = ["123", "4567", ""] 
        # iterates over teh valid extensions & tests them
        for ext in valid_extensions:
            phone = Phone.objects.create(phone_number="3306742811", extension=ext)
            self.assertEqual(phone.extension, ext)

    def test_extension_invalid_formats(self):
        """Tests that invalid extensions lead to a ValidationError"""
        invalid_extensions = [
            "abc",  
            "12345a",  
            "12-34",  
        ]
        # iterates over invalid extensions
        for ext in invalid_extensions:
            phone = Phone(phone_number="3306742811", extension=ext)
            with self.assertRaises(ValidationError):
                phone.full_clean()  

    def test_phone_type_valid_choices(self):
            """Tests that valid phone_type choices are accepted."""
            valid_choices = ["CELL", "HOME", "WORK", "FARM"]
            for choice in valid_choices:
                phone = Phone.objects.create(phone_number="3306742811", phone_type=choice)
                self.assertEqual(phone.phone_type, choice)

    def test_phone_type_invalid_choice(self):
        """Tests that invalid phone_type choices raise a ValidationError"""
        phone = Phone(phone_number="3306742811", phone_type="INVALID")
        with self.assertRaises(ValidationError):
            phone.full_clean() 

    def test_phone_type_saved_and_retrieved_from_db(self):
        """Tests that phone_type can be saved to and then retrieved from the db"""
        phone = Phone.objects.create(phone_number="3306742811", phone_type="CELL")
        retrieved_phone = Phone.objects.get(id=phone.id)
        self.assertEqual(retrieved_phone.phone_type, "CELL")
        
    def test_boolean_fields_default_values(self):
        """Tests that boolean fields for the Phone model default to True."""
        phone = Phone.objects.create(phone_number="3306742811")
        self.assertTrue(phone.can_call)
        self.assertTrue(phone.can_text)
        self.assertTrue(phone.can_leave_voicemail)
        self.assertTrue(phone.is_primary)

    def test_boolean_fields_can_be_set_to_false(self):
        """Tests that boolean fields or the Phone model  can be set to False."""
        phone = Phone.objects.create(
            phone_number="3306742811",
            can_call=False,
            can_text=False,
            can_leave_voicemail=False,
            is_primary=False,
        )
        self.assertFalse(phone.can_call)
        self.assertFalse(phone.can_text)
        self.assertFalse(phone.can_leave_voicemail)
        self.assertFalse(phone.is_primary)

    def test_boolean_fields_can_be_set_to_true(self):
        """Tests that boolean fields or the Phone model can be set to True."""
        phone = Phone.objects.create(
            phone_number="3306742811",
            can_call=True,
            can_text=True,
            can_leave_voicemail=True,
            is_primary=True,
        )
        self.assertTrue(phone.can_call)
        self.assertTrue(phone.can_text)
        self.assertTrue(phone.can_leave_voicemail)
        self.assertTrue(phone.is_primary)

    def test_boolean_fields_saved_and_retrieved_from_db(self):
        """Tests that boolean fields are saved to and can be retrieved from the database."""
        phone = Phone.objects.create(
            phone_number="3306742811",
            can_call=False,
            can_text=True,
            can_leave_voicemail=False,
            is_primary=True,
        )
        retrieved_phone = Phone.objects.get(id=phone.id)
        self.assertFalse(retrieved_phone.can_call)
        self.assertTrue(retrieved_phone.can_text)
        self.assertFalse(retrieved_phone.can_leave_voicemail)
        self.assertTrue(retrieved_phone.is_primary)

class ContactMethodModelTestCase(TestCase):

    def setUp(self):
        """
        Set up test data for the ContactMethod model by setting a method_name and creating a contact method.
        """
        self.contact_method = ContactMethod.objects.create(
            method_name="Email",
        )

    def test_contact_method_creation(self):
        """
        Test that a ContactMethod instance is created correctly.
        """
        self.assertEqual(self.contact_method.method_name, "Email")

    def test_contact_method_str_method(self):
        """
        Test the __str__ method of the ContactMethod model.
        """
        self.assertEqual(str(self.contact_method), "Email")

    def test_method_name_uniqueness(self):
        """
        Test that the method_name field is unique.
        """
        with self.assertRaises(IntegrityError):
            ContactMethod.objects.create(method_name="Email")  # Duplicate method_name

    def test_method_name_max_length(self):
        """
        Test that the method_name field does not exceed the maximum length of 20 characters.
        """
        # Test with a valid length (20 characters is the max. length)
        valid_method_name = "T" * 20
        contact_method = ContactMethod.objects.create(method_name=valid_method_name)
        self.assertEqual(contact_method.method_name, valid_method_name)

        # Test with an invalid length for the contact method
        invalid_method_name = "T" * 21
        contact_method = ContactMethod(method_name=invalid_method_name)
        with self.assertRaises(ValidationError):
            contact_method.full_clean()  

    def test_method_name_blank_or_null(self):
        """
        Test that the method_name field cannot be blank or null.
        """
        with self.assertRaises(ValidationError):
            contact_method = ContactMethod(method_name="")
            contact_method.full_clean()  

        with self.assertRaises(IntegrityError):
            ContactMethod.objects.create(method_name=None)  

    def test_method_name_help_text(self):
        """
        Test that the help_text for the method_name field is correctly defined.
        """
        field = ContactMethod._meta.get_field("method_name")
        self.assertEqual(
            field.help_text,
            "Preferred Contact Method: phone, email, text, voicemail, etc."
        )