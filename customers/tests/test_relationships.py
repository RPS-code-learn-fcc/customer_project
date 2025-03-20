from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import timezone
from datetime import datetime, timedelta, timezone as datetime_timezone
from app_users.models import CustomUser
from customers.models import (
    CustomerDocument,
    CustomerNote,
    CustomerInterest,
    CustomerMailingList,
    CustomerNoteHistory,
    CustomerDocumentHistory,
    Customer,
    Address,
)

import os

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator

class CustomerDocumentModelTestCase(TestCase):
    def setUp(self):
        """
            Set up test data to test the CustomerDocument model by creating a user, customer, and both valid & invalid test files.
        """
        # create a user
        self.user = CustomUser.objects.create_user(
            email="test@test.com",
            password="testpassword123",
        )
        # create a customer
        self.customer = Customer.objects.create(
            first_name="Sally",
            last_name="Mae",
            customer_type="person",
            creator=self.user,
        )

        # Create Valid files: pdf, doc, docx by using SimpleUploadedFile and file MIME types
        self.valid_pdf = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf",
        )
        self.valid_doc = SimpleUploadedFile(
            "test_file.doc",
            b"file_content",
            content_type="application/msword",
        )
        self.valid_docx = SimpleUploadedFile(
            "test_file.docx",
            b"file_content",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        # Create Invalid files: jpeg, png, mpeg by using SimpleUploadedFile and file MIME types
        self.invalid_image_jpeg = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg",
        )
        self.invalid_image_png = SimpleUploadedFile(
            "test_image.png",
            b"file_content",
            content_type="image/png",
        )
        self.invalid_audio = SimpleUploadedFile(
            "test_audio.mp3",
            b"file_content",
            content_type="audio/mpeg",
        )

    def test_customer_document_creation_valid_pdf(self):
        """
        Test that CustomerDocument instances are created correctly with a valid file type - pdf.
        """
        # Test PDF
        document_pdf = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test PDF document",
            author=self.user,
            customer=self.customer,
        )
        document_pdf.full_clean()  # validate the instance
        document_pdf.save()# save the instance to the db
        
        # get the newly saved CustomerDocument instance from the db
        saved_document = CustomerDocument.objects.get(id=document_pdf.id)
        
        # Assertions with descriptive messages
        self.assertEqual(saved_document.file_type, "w9", "The file_type should be 'w9'.")
        self.assertEqual(saved_document.file_detail, "Test PDF document", "The file_detail should be 'Test PDF document'.")
        self.assertEqual(saved_document.author, self.user, "The document author should match the test user.")
        self.assertEqual(saved_document.customer, self.customer, "The document customer should match the test customer.")
        
        # Check the file field
        self.assertEqual(saved_document.file.name, document_pdf.file.name, "The file name should equal the uploaded file name.")
        self.assertEqual(saved_document.file.read(), b"file_content", "The file content should equal the uploaded file content.")

    def test_customer_document_creation_valid_doc(self):
        """
            Tests that a CustomerDocument instance is created correctly with a valid file type - doc.
        """
        # Create a CustomerDocument instance with a valid DOC file
        document_doc = CustomerDocument(
            file=self.valid_doc,
            file_type="w9",
            file_detail="Test DOC document",
            author=self.user,
            customer=self.customer,
        )
        
        # Validate the instance 
        document_doc.full_clean()
        
        # Save the instance to the db
        document_doc.save()
        
        # get the saved instance from the db
        saved_document = CustomerDocument.objects.get(id=document_doc.id)
        
        # Assertions w/ msgs
        self.assertEqual(saved_document.file_type, "w9", "The file_type should be 'w9'.")
        self.assertEqual(saved_document.file_detail, "Test DOC document", "The file_detail should be 'Test DOC document'.")
        self.assertEqual(saved_document.author, self.user, "The author should equal the test user.")
        self.assertEqual(saved_document.customer, self.customer, "The customer should equal the test customer.")
        
        # Check the file field name
        self.assertEqual(saved_document.file.name, document_doc.file.name, "The file name should equal the uploaded file name.")
        self.assertEqual(saved_document.file.read(), b"file_content", "The file content should equal the uploaded file content.")

    def test_customer_document_creation_valid_docx(self):
        """
            Test that a CustomerDocument instance is created correctly with a valid file type - docx.
        """
        # Create a CustomerDocument instance with a valid DOCX file
        document_docx = CustomerDocument(
            file=self.valid_docx,
            file_type="w9",
            file_detail="Test DOCX document",
            author=self.user,
            customer=self.customer,
        )
        
        # Validate the instance 
        document_docx.full_clean()
        
        # Save the instance to the db
        document_docx.save()
        
        # get newly saved instance from the db
        saved_document = CustomerDocument.objects.get(id=document_docx.id)
        
        # Assertions w/ msgs
        self.assertEqual(saved_document.file_type, "w9", "The file_type should be 'w9'.")
        self.assertEqual(saved_document.file_detail, "Test DOCX document", "The file_detail should be 'Test DOCX document'.")
        self.assertEqual(saved_document.author, self.user, "The author should match the test user.")
        self.assertEqual(saved_document.customer, self.customer, "The customer should match the test customer.")
        
        # Check the file field
        self.assertEqual(saved_document.file.name, document_docx.file.name, "The file name should match the uploaded file name.")
        self.assertEqual(saved_document.file.read(), b"file_content", "The file content should match the uploaded file content.")

    def test_customer_document_creation_invalid_files(self):
        """
            Test that CustomerDocument instances with invalid file types raise a ValidationError.
        """
        # Test JPEG
        with self.assertRaises(ValidationError):
            document_jpeg = CustomerDocument(
                file=self.invalid_image_jpeg,
                file_type="w9",
                file_detail="Test JPEG image",
                author=self.user,
                customer=self.customer,
            )
            document_jpeg.full_clean()  

        # Test PNG
        with self.assertRaises(ValidationError):
            document_png = CustomerDocument(
                file=self.invalid_image_png,
                file_type="w9",
                file_detail="Test PNG image",
                author=self.user,
                customer=self.customer,
            )
            document_png.full_clean()  

        # Test MP3
        with self.assertRaises(ValidationError):
            document_mp3 = CustomerDocument(
                file=self.invalid_audio,
                file_type="w9",
                file_detail="Test MP3 audio",
                author=self.user,
                customer=self.customer,
            )
            document_mp3.full_clean()  

    def test_customer_document_str_method_file_detail_entered(self):
        """
            Tests the __str__ method of the CustomerDocument model: Returns the File Name & Description or just the file name
        """
        document = CustomerDocument.objects.create(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test document",
            author=self.user,
            customer=self.customer,
        )
        # Extract the dynamically generated file name
        file_name = os.path.basename(document.file.name)
        # Check that file name is formated correctly and as a string
        self.assertEqual(str(document), f"{file_name} - Desc: Test document")
        
    def test_customer_document_str_method_no_file_detail_entered(self):
        """
            Tests the __str__ method of the CustomerDocument model: Returns the File Name & Description or just the file name
        """
        document = CustomerDocument.objects.create(
            file=self.valid_pdf,
            file_type="w9",
            author=self.user,
            customer=self.customer,
        )
        # Extract the dynamically generated file name
        file_name = os.path.basename(document.file.name)
        # Check that file name is formated correctly and as a string
        self.assertEqual(str(document), f"{file_name}")

    def test_customer_document_clean_method_valid(self):
        """
        Test the clean method for a valid CustomerDocument instance.
        """
        document = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test document",
            author=self.user,
            customer=self.customer,
        )
        document.clean()  # no error should be raised

    def test_customer_document_clean_method_invalid(self):
        """
        Test the clean method for an invalid CustomerDocument instance- Must provide file_detail if the file_type is other.
        """
        document = CustomerDocument(
            file=self.valid_pdf,
            file_type="other",
            file_detail="",
            author=self.user,
            customer=self.customer,
        )
        with self.assertRaises(ValidationError):
            document.clean() # an error will be raised as the filed detail cannot be missing
    
    def test_file_type_choices(self):
        """
            Tests that only valid file types can be selected for the file_type field.
        """
        # List of valid file types from FILE_TYPES
        valid_file_types = [choice[0] for choice in CustomerDocument.FILE_TYPES]
        
        # Test valid file types
        for file_type in valid_file_types:
            document = CustomerDocument(
                file=self.valid_pdf,  # Use any valid file for testing
                file_type=file_type,
                file_detail=f"Test {file_type} document",
                author=self.user,
                customer=self.customer,
            )
            document.full_clean()  
            document.save()
            self.assertEqual(document.file_type, file_type, f"The file_type should be '{file_type}'.")

        # Test an invalid file type
        invalid_file_type = "invalid_file_type"
        with self.assertRaises(ValidationError, msg=f"Invalid file type '{invalid_file_type}' should raise a ValidationError."):
            document = CustomerDocument(
                file=self.valid_pdf,  # Use any valid file for testing
                file_type=invalid_file_type,
                file_detail="Test invalid file type document",
                author=self.user,
                customer=self.customer,
            )
            document.full_clean()  # Should raise a ValidationError

    def test_file_detail_field(self):
        """
            Tests the file_detail field of the CustomerDocument model.
        """
        # Test with a valid file_detail (non-empty string)
        valid_file_detail = "This is a valid file description."
        document_with_detail = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail=valid_file_detail,
            author=self.user,
            customer=self.customer,
        )
        document_with_detail.full_clean()  
        document_with_detail.save()
        
        # get newly saved instance from db
        saved_document_with_detail = CustomerDocument.objects.get(id=document_with_detail.id)
        
        # Assertions for valid file_detail
        self.assertEqual(saved_document_with_detail.file_detail, valid_file_detail, "The saved file_detail should equal the original file_detail input value.")

        # Test with an empty file_detail as this field is not required
        document_without_detail = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="",  # Empty string
            author=self.user,
            customer=self.customer,
        )
        document_without_detail.full_clean()  
        document_without_detail.save()
        
        # get newly saved instance from db
        saved_document_without_detail = CustomerDocument.objects.get(id=document_without_detail.id)
        
        # Assertions for empty file_detail
        self.assertEqual(saved_document_without_detail.file_detail, "", "The file_detail field can be blank and should be an empty string if nothing is entered")

        # Test with a file_detail exceeding the maximum length allowed of 100 characters
        invalid_file_detail = "z" * 101  # 101 characters exceeds allowed length
        document_with_long_detail = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail=invalid_file_detail,
            author=self.user,
            customer=self.customer,
        )
        with self.assertRaises(ValidationError, msg="A file_detail exceeding 100 characters should cause a ValidationError"):
            document_with_long_detail.full_clean()  
    
    def test_author_field_of_document(self):
        """
            Tests the author field of the CustomerDocument model.
        """
        # Create a CustomerDocument instance with a valid author
        document_with_author = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test document",
            author=self.user,  # Link to the test user
            customer=self.customer,
        )
        document_with_author.full_clean()  
        document_with_author.save()
        
        # get the saved instance from the database
        saved_document_with_author = CustomerDocument.objects.get(id=document_with_author.id)
        
        # Assertions for valid author
        self.assertEqual(saved_document_with_author.author, self.user, "The author saved document author should match the user.")

    def test_author_blank(self):
        """
            Tests that the author field cannot be blank.
        """
        # try to create a document w/o an authoer
        document_without_author = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test document",
            author=None,  
            customer=self.customer,
        )
        
        # a validation error should be raised
        with self.assertRaises(ValidationError, msg="The author field cannot be blank."):
            document_without_author.full_clean()  

    def test_customer_field(self):
        """
            Tests the customer field of the CustomerDocument model.
        """
        # Test creating a CustomerDocument with a valid customer
        document_with_customer = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test document",
            author=self.user,
            customer=self.customer,  # Link to the test customer
        )
        document_with_customer.full_clean()  
        document_with_customer.save()
        
        # get save instance from db
        saved_document_with_customer = CustomerDocument.objects.get(id=document_with_customer.id)
        
        # make sure it is a valid cstomer
        self.assertEqual(saved_document_with_customer.customer, self.customer, "The saved customer should match the test customer.")

        # if not customer is provided - a validation error occurrs
        document_without_customer = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test document",
            author=self.user,
            customer=None,  # No customer 
        )
        with self.assertRaises(ValidationError, msg="The customer field cannot be blank."):
            document_without_customer.full_clean()  

        # Test the CASCADE on_delete behavior
        self.customer.delete()  # Delete the linked Customer
        
        # Verify that the associated CustomerDocument is also deleted
        with self.assertRaises(CustomerDocument.DoesNotExist, msg="If the customer is deleted, the linked document should also be deleted"):
            CustomerDocument.objects.get(id=document_with_customer.id)

    def test_created_at_field(self):
        """
            Tests the created_at field of the CustomerDocument model.
        """
        # Create a CustomerDocument instance
        document = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test document",
            author=self.user,
            customer=self.customer,
        )
        document.full_clean()  
        document.save()
        
        # get newly saved instance from db
        saved_document = CustomerDocument.objects.get(id=document.id)
        
        # created_at should not be null
        self.assertIsNotNone(saved_document.created_at, "The created_at field should not be null.")
        
        # test the timestamp saved is approximately the current time to allow for a lag in time saved
        self.assertAlmostEqual(
            saved_document.created_at,
            timezone.now(),
            delta=timedelta(seconds=1),  # Allow a 1-s time lag
            msg="The created_at field should be set to the current timestamp."
        )

        # Test that the timestamp cannot be overwrote 
        manual_timestamp = datetime(2023, 1, 1, tzinfo=datetime_timezone.utc)  
        
        # try to manually set time
        document_with_manual_timestamp = CustomerDocument(
            file=self.valid_pdf,
            file_type="w9",
            file_detail="Test document",
            author=self.user,
            customer=self.customer,
            created_at=manual_timestamp,  
        )
        document_with_manual_timestamp.save()
        
        # get the saved instance from the db
        saved_document_with_manual_timestamp = CustomerDocument.objects.get(id=document_with_manual_timestamp.id)
        
        # Assertions for manual created_at
        self.assertNotEqual(
            saved_document_with_manual_timestamp.created_at,
            manual_timestamp,
            "The created_at field should not be manually set."
        )

class CustomerNoteModelTestCase(TestCase):
    def setUp(self):
        """
            Set up test data: customer & user for the CustomerNote model.
        """
        self.user = CustomUser.objects.create_user(
            email="test@test.com",
            password="testpassword123",
        )
        self.customer = Customer.objects.create(
            first_name="Sally",
            last_name="Mae",
            customer_type="person",
            creator=self.user,
        )

    def test_customer_note_creation(self):
        """
            Tests that a CustomerNote instance is created without errors.
        """
        note = CustomerNote.objects.create(
            note="This is a test note.",
            author=self.user, # associate the note with a user
            customer=self.customer, # associate the note with a customer
        )
        self.assertEqual(note.note, "This is a test note.")
        self.assertEqual(note.author, self.user, msg="The note author should be the same as the test user.")
        self.assertEqual(note.customer, self.customer, msg="The note customer should be the same as the test customer.")
        
    def test_created_at_field(self):
        """
            Test the created_at field of the CustomerNote model: cannot manually update it and that the timestamp is set to the current time.
        """
        # Create a CustomerNote instance
        customer_note = CustomerNote(
            note="This is a test note.",
            author=self.user,
            customer=self.customer,
        )
        # makes sure no errors are raised & it is saved to the db
        customer_note.full_clean()  
        customer_note.save()
        
        # get newly saved instance from the db
        saved_customer_note = CustomerNote.objects.get(id=customer_note.id)
        
        # make sure the created_at time is not none as it should be added automatically
        self.assertIsNotNone(saved_customer_note.created_at, "The created_at field should not be null.")
        self.assertAlmostEqual(
            saved_customer_note.created_at,
            timezone.now(),
            delta=timedelta(seconds=1),  # a 1s time deviaiton is allowed
            msg="The created_at field should be the current time within a 1s time difference."
        )

        # Test that created_at cannot be manually set
        manual_timestamp = datetime(2020, 1, 1, tzinfo=datetime_timezone.utc) 
        customer_note_with_manual_timestamp = CustomerNote(
            note="This is another test note.",
            author=self.user,
            customer=self.customer,
            created_at=manual_timestamp,  
        )
        customer_note_with_manual_timestamp.save()
        
        # get the newly created instance from the db
        saved_customer_note_with_manual_timestamp = CustomerNote.objects.get(id=customer_note_with_manual_timestamp.id)
        
        # test the manual setting of the time
        self.assertNotEqual(
            saved_customer_note_with_manual_timestamp.created_at,
            manual_timestamp,
            msg="The created_at field should not be manually set."
        )
        
    def test_author_field_of_note(self):
        """
            Tests the author field of the CustomerNote model.
        """
        # Create a CustomerNote instance with a valid author
        note_with_author = CustomerNote(
            note="Test note text here.",
            author=self.user,  # Link to the test user
            customer=self.customer,
        )
        note_with_author.full_clean()  
        note_with_author.save()
        
        # get the saved instance from the database
        saved_note_with_author = CustomerNote.objects.get(id=note_with_author.id)
        
        # Assertions for valid author
        self.assertEqual(saved_note_with_author.author, self.user, "The  saved document note should be the same as the test user.")

    def test_author_blank(self):
        """
            Tests that the author field cannot be blank of a CustomerNote Instsance.
        """
        # try to create a note w/o an author
        note_without_author = CustomerNote(
            note="Test note text here.",
            author=None,  
            customer=self.customer,
        )
        
        # a validation error should be raised
        with self.assertRaises(ValidationError, msg="The author field cannot be blank."):
            note_without_author.full_clean()  

    def test_customer_note_str_method(self):
        """
            Test the __str__ method for the CustomerNote model: it should return the first 30 characters of the note & the date & time it was created.
        """
        # set the note text
        note_text = "This is a test note for the CustomerNote model."
        
        # create a CustomerNote instance
        customer_note = CustomerNote(
            note=note_text,
            author=self.user,
            customer=self.customer,
        )
        
        # check that no errors are raised & save it to the db
        customer_note.full_clean() 
        customer_note.save()
        
        # get the newly saved instance from the db
        saved_customer_note = CustomerNote.objects.get(id=customer_note.id)
        
        # expected __str__ representation
        expected_str = f"{note_text[:30]}... ({saved_customer_note.created_at.strftime('%B %d, %Y, %I:%M %p')})"
        
        # test that the expected is the same as the outcome
        self.assertEqual(str(saved_customer_note), expected_str, "The __str__ method should return the expected string representation.")

    def test_customer_field(self):
        """
            Test the customer field of the CustomerNote model.
        """
        # Test creating a CustomerNote with a valid customer
        customer_note_with_customer = CustomerNote(
            note="This is a test note.",
            author=self.user,
            customer=self.customer, 
        )
        customer_note_with_customer.full_clean()  
        customer_note_with_customer.save()
        
        # gwt the newly saved note instance from the database
        saved_customer_note_with_customer = CustomerNote.objects.get(id=customer_note_with_customer.id)
        
        # Make sure a valid customer is saved
        self.assertEqual(saved_customer_note_with_customer.customer, self.customer, "The saved note.customer should be the same as the test customer.")

        # Test creating a CustomerNote without a customer 
        customer_note_without_customer = CustomerNote(
            note="This is another test note.",
            author=self.user,
            customer=None,  # No customer 
        )
        with self.assertRaises(ValidationError, msg="The customer field cannot be blank."):
            customer_note_without_customer.full_clean()  

        # Test the on_delete behavior (CASCADE)
        self.customer.delete()  # Delete the linked Customer
        
        # Verify that the associated CustomerNote is also deleted
        with self.assertRaises(CustomerNote.DoesNotExist, msg="The CustomerNote should be deleted when the linked Customer is deleted."):
            CustomerNote.objects.get(id=customer_note_with_customer.id)
    
    def test_customer_note_ordering(self):
        """
            Tests that CustomerNote instances are correctly ordered by the Meta property: -created_at (most recent note is first).
        """
        # Create timestamps for testing
        now = timezone.now()
        older_time = now - timedelta(days=1)
        newer_time = now + timedelta(days=1)

        # Create CustomerNote instances with different created_at timestamps
        note_older = CustomerNote.objects.create(
            note="This is an older note.",
            author=self.user,
            customer=self.customer,
            created_at=older_time,
        )
        note_now = CustomerNote.objects.create(
            note="This is a current note.",
            author=self.user,
            customer=self.customer,
            created_at=now,
        )
        note_newer = CustomerNote.objects.create(
            note="This is a newer note.",
            author=self.user,
            customer=self.customer,
            created_at=newer_time,
        )

        # gets alll notes that should be ordered with the most recent note, first
        ordered_notes = CustomerNote.objects.all()

        # checks the ordering of the notes
        self.assertEqual(ordered_notes[0], note_newer, msg="The newest note should be first.")
        self.assertEqual(ordered_notes[1], note_now, msg="The current note should be second.")
        self.assertEqual(ordered_notes[2], note_older, msg="The oldest note should be last.")
        
    def test_note_number_property(self):
        """
            Tests the note_number property of the CustomerNote model.
        """
        # Create multiple CustomerNote instances for the same customer
        note1 = CustomerNote.objects.create(
            note="This is the first note.",
            author=self.user,
            customer=self.customer,
        )
        note2 = CustomerNote.objects.create(
            note="This is the second note.",
            author=self.user,
            customer=self.customer,
        )
        note3 = CustomerNote.objects.create(
            note="This is the third note.",
            author=self.user,
            customer=self.customer,
        )

        # Test the note_number property for each note
        self.assertEqual(note1.note_number, 1, msg="The first note should have note_number of 1.")
        self.assertEqual(note2.note_number, 2, msg="The second note should have note_number of 2.")
        self.assertEqual(note3.note_number, 3, msg="The third note should have note_number =of3.")

        # Create a note for a different customer
        new_customer = Customer.objects.create(
            first_name="Jane",
            last_name="Doe",
            customer_type="person",
            creator=self.user,
        )
        note_for_new_customer = CustomerNote.objects.create(
            note="This is a test note for a new customer",
            author=self.user,
            customer=new_customer,
        )

        # Test the note_number property for the note belonging to another customer
        self.assertEqual(note_for_new_customer.note_number, 1, msg="The note for the new customer should have note_numberof 1.")


class CustomerInterestModelTestCase(TestCase):
    def setUp(self):
        """
            Sets up test data: an interest for the CustomerInterest model.
        """
        self.interest = CustomerInterest.objects.create(
            name="Soil Tests",
            slug="soiltests",
        )
    def test_setup_creates_customer_interest(self):
        """
          Tests that the setUp method succesfully creates a new CustomerInterest instance.
        """
        self.assertTrue(CustomerInterest.objects.filter(id=self.interest.id).exists(), msg="The CustomerInterest instance exists in the db.")

        # Verify fields are as expected in the newly created instance
        self.assertEqual(self.interest.name, "Soil Tests", msg="The name should be 'Soil Tests'.")
        self.assertEqual(self.interest.slug, "soiltests", msg="The slug should be 'soiltests'.")
        
        self.assertFalse(self.interest.icon_image, msg="The icon_image field should be empty if now specified")
    
    def test_name_field_valid(self):
        """
            Tests that the name field accepts valid input based upon the validation requirements as definied in the relationships.py file for the CustomerInterest.name fiel.
        """
        # create a list of valid names
        valid_names = [
            "Tree Sale",
            "Soil-Tests",
            "Cover Crops 2023",
            "1234-Test",
        ]
        # loop through the valid names in the list
        for name in valid_names:
            interest = CustomerInterest(name=name, slug="slug")
            interest.full_clean()  # all of these interest names should be accepted as valid interests names (w/o errors)


    def test_name_field_invalid(self):
        """
            Tests that the name field of the CustomerInterest raises ValidationError for invalid names.
        """
        # create a list of invalid names
        invalid_names = [
            "R",  # Too short (less than 4 characters)
            "t" * 51,  # Too long (more than 50 characters)
            "Invalid@Name",  # Invalid characters (@)
            "Invalid#Name",  # Invalid characters (#)
        ]
        # loops through invalid list of names and sees if expected validation errors occur
        for name in invalid_names:
            interest = CustomerInterest(name=name, slug="slug")
            with self.assertRaises(ValidationError, msg=f"Name '{name}' should raise a ValidationError as it is an invalid input."):
                interest.full_clean()  

    def test_name_field_unique(self):
        """
            Tests that the interest name field enforces uniqueness.
        """
        # Attempt to create another CustomerInterest with the same name and this raises an error
        with self.assertRaises(ValidationError, msg="The name field must be unqique"):
            duplicate_interest = CustomerInterest(name="Soil Tests", slug="anotherslug")
            duplicate_interest.full_clean()  

    def test_customer_interest_str_method(self):
        """
            Tests the __str__ method of the CustomerInterest model.
        """
        self.assertEqual(str(self.interest), "Soil Tests")

    def test_icon_image_field_optional(self):
        """
         Tests that the icon_image field is optional.
        """
        # Validates & saves interest instance
        self.interest.full_clean()  
        self.interest.save()
        
        # gets tge saved interest instance from the database
        saved_interest_without_icon = CustomerInterest.objects.get(id=self.interest.id)
        
        self.assertFalse(saved_interest_without_icon.icon_image, msg= "The icon_image field should be empty when not provided.")
    
    def test_icon_image_field_valid(self):
        """
            Tests that the icon_image field accepts valid file uploads.
        """
        # Create a SimpleUploadedFile for testing
        icon_file = SimpleUploadedFile(
            name="test_icon.png",
            content=b"file_content",
            content_type="image/png",
        )
        

        self.interest.icon_image = icon_file
        self.interest.full_clean()  
        self.interest.save()
        
        # gets the saved instance from the db
        saved_interest_with_icon = CustomerInterest.objects.get(id=self.interest.id)
        
        self.assertIsNotNone(saved_interest_with_icon.icon_image, msg="The icon_image field should not be null when provided.")
        
        # see if file name starts with the expected path
        self.assertTrue(
            saved_interest_with_icon.icon_image.name.startswith("icons/test_icon"),
            f"The icon_image file name should start with 'icons/test_icon'. Actual Name: {saved_interest_with_icon.icon_image.name}"
        )    
    def test_slug_field_valid(self):
        """
            Tests that the slug field accepts valid input.
        """
        # creates a list of valid slugs
        valid_slugs = [
            "tree-sale",
            "soil-tests",
            "cover-crops-2023",
            "1234-test",
        ]
        # iterates over the list of slugs & no errors should be raised
        for slug in valid_slugs:
            interest = CustomerInterest(name="Test Interest", slug=slug)
            interest.full_clean()  

    def test_slug_field_invalid(self):
        """
            Tests that the slug field raises ValidationError for invalid input.
        """
        # create a list of invalid slugs
        invalid_slugs = [
            "xyc",  # Too short (less than 4 characters)
            "a" * 21,  # Too long (more than 20 characters)
            "invalid@slug",  # Invalid characters (@)
            "invalid#slug",  # Invalid characters (#)
            "invalid slug",  # Invalid characters (space)
        ]
        # loop over the slugs and raise validation errors for theinputs
        for slug in invalid_slugs:
            interest = CustomerInterest(name="Test Interest", slug=slug)
            with self.assertRaises(ValidationError, msg=f"Slug '{slug}' should raise a ValidationError."):
                interest.full_clean()  

    def test_slug_field_unique(self):
        """
            Tests that slug names are unique
        """
        # cannot create another slug with the same name as an already existing instance with the same name
        with self.assertRaises(ValidationError, msg="The slug field should enforce uniqueness."):
            duplicate_interest = CustomerInterest(name="Another Interest", slug="soiltests")
            duplicate_interest.full_clean()  
            
    def test_customer_interest_ordering(self):
        """
        Tests that CustomerInterest instances are ordered alphabetically by name.
        """
        # Create CustomerInterest instances with different names
        interest1 = CustomerInterest.objects.create(
            name="Summer Camp",
            slug="summer-camp",
        )
        interest2 = CustomerInterest.objects.create(
            name="Cover Crops",
            slug="cover-crops",
        )
        interest3 = CustomerInterest.objects.create(
            name="Tree Sale",
            slug="tree-sale",
        )

        # Retrieve all CustomerInterest instances ordered by name
        ordered_interests = CustomerInterest.objects.all()

        # Expected order (alphabetical by name)
        expected_order = [interest2, self.interest, interest1, interest3]  # Cover Crops, Soil Tests, Summer Camp, Tree Sale

        self.assertEqual(list(ordered_interests), expected_order, "CustomerInterest instances should be ordered alphabetically by name.")
    
    def test_icon_image_url_property(self):
        """
        Test the icon_image_url property of the CustomerInterest model.
        """
        # Test when icon_image is not provided (should return default icon URL)
      
        default_icon_url = staticfiles_storage.url('images/star.svg')
        self.assertEqual(self.interest.icon_image_url, default_icon_url, "The icon_image_url should return the default icon URL as no URL is specified for self.interest")

        # Test when icon_image is provided (should return the icon_image URL)
        icon_file = SimpleUploadedFile(
            name="test_icon.png",
            content=b"file_content",
            content_type="image/png",
        )
        interest_with_icon = CustomerInterest.objects.create(
            name="Cover Crops",
            slug="cover-crops",
            icon_image=icon_file,
        )
        # assert that the uploaded icon's path matches the saved instance's url 
        self.assertTrue(
            interest_with_icon.icon_image_url.startswith("/media/icons/test_icon"),
            f"The icon_image_url should return the URL of the uploaded icon_image. Actual: {interest_with_icon.icon_image_url}"
        )
class CustomerMailingListModelTestCase(TestCase):
    def setUp(self):
        """
         Sets up test data: creates a mailing list for the CustomerMailingList model.
        """
        # Create a user
        self.user = CustomUser.objects.create_user(
            email="test@test.com",
            password="testpassword123",
        )
        
        # Create a CustomerMailingList instance
        self.mailing_list = CustomerMailingList.objects.create(
            name="Fish Sale",
        )
        
        # Create customers
        self.customer1 = Customer.objects.create(
            first_name="John",
            last_name="Smith",
            customer_type="person",
            creator=self.user,
        )
        self.customer2 = Customer.objects.create(
            first_name="Kelly",
            last_name="Miller",
            customer_type="person",
            creator=self.user,
        )
        
        # Create addresses
        self.address1 = Address.objects.create(
            street="123 Main St",
            city="Millersburg",
            state="IL",
            zip_code="11111",
        )
        self.address2 = Address.objects.create(
            street="123 Chestnut St",
            city="Jacksonville",
            state="FL",
            zip_code="12345",
        )
        
        # Create interests
        self.interest1 = CustomerInterest.objects.create(
            name="Soil Tests",
            slug="soiltests",
        )
        self.interest2 = CustomerInterest.objects.create(
            name="Tree Sale",
            slug="tree-sale",
        )
        
        # Add an interest to satisfy the custom clean method in the model
        self.mailing_list.interests.add(self.interest1)  

    def test_setup_creates_mailing_list(self):
        """
            Tests that the setUp method successfully creates a CustomerMailingList instance.
        """
        # Check that the mailing list instance exists in db
        self.assertTrue(CustomerMailingList.objects.filter(id=self.mailing_list.id).exists(), msg="The CustomerMailingList does exist.")

        # Cchecks attributes of newly created instance in db
        self.assertEqual(self.mailing_list.name, "Fish Sale", "The mailing list name should be 'Fish Sale'.")
        self.assertIsNotNone(self.mailing_list.created_at, "The created_at field shouldn't be null.")

    def test_name_field_valid(self):
            """
                Tests that the name field accepts valid inputs as defined in the relationships.py file.
            """
            # Create a list of valid mailing list names
            valid_names = [
                "Summer Camp",
                "Fish-Sale",
                "Cover Crops 2023",
                "1234-Test",
            ]
            # Iterate over valid names and ensure no errors are raised
            for name in valid_names:
                mailing_list_valid = CustomerMailingList(name=name)
                # save and add interest for full_clean() to work
                mailing_list_valid.save()
                mailing_list_valid.interests.add(self.interest1)  
                mailing_list_valid.full_clean()  

    def test_name_field_invalid(self):
        """
            Tests that the name field raises ValidationError for invalid inputa.
        """
        # Invalid names list
        invalid_names = [
            "Y",  
            "M" * 51,  
            "Invalid@Name",  
            "Invalid#Name",  
        ]
        # Iterate through the list of invalid names - should produce a validation error for each invalid name
        for name in invalid_names:
            mailing_list = CustomerMailingList(name=name)
            with self.assertRaises(ValidationError, msg=f"Name '{name}' should raise a ValidationError."):
                mailing_list.full_clean()  

    def test_name_field_unique(self):
        """
            Tests that the name field is unique.
        """
        # Attempt to create another CustomerMailingList with the same name as an already existing instance
        with self.assertRaises(ValidationError, msg="The name field must be unique. A mailing list instance already exists with this name."):
            duplicate_mailing_list = CustomerMailingList(name="Fish Sale")
            duplicate_mailing_list.full_clean() 

    def test_customers_field(self):
        """
            Tests the customers field of the CustomerMailingList model.
        """
        # Add customers to the mailing list, 'Fish Sale' & then save teh uupdated instance
        self.mailing_list.customers.add(self.customer1, self.customer2)
        self.mailing_list.save()  

        # get saved instance from the db
        saved_mailing_list_with_customers = CustomerMailingList.objects.get(id=self.mailing_list.id)
        
        self.assertEqual(saved_mailing_list_with_customers.customers.count(), 2, msg="There should be 2 customers that have been added to the mailing list 'Fish Sale'.")
        self.assertIn(self.customer1, saved_mailing_list_with_customers.customers.all(), msg="Customer1 should be in the customers field of the list.")
        self.assertIn(self.customer2, saved_mailing_list_with_customers.customers.all(), msg="Customer2 should be in the customers field of the list.")
    
    def test_addresses_field(self):
        """
            Tests the inputs for the addresses field of the CustomerMailingList model.
        """
        # Add addresses to the mailing list, 'Fish Sale'
        self.mailing_list.addresses.add(self.address1, self.address2)
        self.mailing_list.full_clean()  
        self.mailing_list.save()
        
        # get newly saved instance from the db
        saved_mailing_list = CustomerMailingList.objects.get(id=self.mailing_list.id)
        
        # Assertions for addresses field
        self.assertEqual(saved_mailing_list.addresses.count(), 2, "The addresses field should contain 2 addresses in the mailing list 'Fish Sale'.")
        self.assertIn(self.address1, saved_mailing_list.addresses.all(), "Address1 should be included in the addresses field of the mailing list.")
        self.assertIn(self.address2, saved_mailing_list.addresses.all(), "Address2 should be included in the addresses field of the mailing list.")

    def test_created_at_field(self):
        """
            Tests that the created_at field is automatically created & populated w/ the current time
        """
        # get the newly saved instance from the db
        saved_mailing_list = CustomerMailingList.objects.get(id=self.mailing_list.id)
        
        # created_at field cannot be null
        self.assertIsNotNone(saved_mailing_list.created_at, msg="The created_at field should not be null.")
        self.assertAlmostEqual(
            saved_mailing_list.created_at,
            timezone.now(),
            delta=timezone.timedelta(seconds=1),  
            msg="The created_at field should be set to the current timestamp within a 1s time period."
        )

    def test_clean_method(self):
        """
            Tests the clean method: an interest or address must be included
        """
        
        # Create and save a CustomerMailingList instance with no addresses or interests
        invalid_mailing_list = CustomerMailingList(name="Invalid MailingList")
        invalid_mailing_list.save()  
        
        # Verify that the clean method raises a ValidationError
        with self.assertRaises(ValidationError, msg="The clean method will reutrn a validation error is no addrss or interest is provided"):
            invalid_mailing_list.full_clean()

    def test_str_method(self):
        """
            Tests the __str__ method of CustomerMailingList
        """
        saved_mailing_list = CustomerMailingList.objects.get(id=self.mailing_list.id)
        
        # test string method
        self.assertEqual(str(saved_mailing_list), "Fish Sale", msg="The __str__ method should return the mailing list's name")

    def test_meta_ordering(self):
        """
            Tests the Meta class's ordering attribute to ensure instances are ordered by -created_at.
        """
        # Create more mailing lists (but don't save them to the db)
        mailing_list1 = CustomerMailingList.objects.create(
            name="Summer Camp",
        )
        mailing_list2 = CustomerMailingList.objects.create(
            name="Tree Sale",
        )
        
        # Retrieve all CustomerMailingList instances ordered by -created_at
        ordered_mailing_lists = CustomerMailingList.objects.all()
        
        # The expected order of the mailing lists (most recent first)
        expected_order = [mailing_list2, mailing_list1, self.mailing_list]
        
        self.assertEqual(list(ordered_mailing_lists), expected_order, msg="CustomerMailingList instances should be in descending order my creation time")

class CustomerNoteHistoryModelTestCase(TestCase):
    def setUp(self):
        """
            Set up test data for CustomerNoteHistory Model: user, customer, customer note, and customer note history.
        """
        # Create a CustomUser
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )
        # create a customer
        self.customer = Customer.objects.create(
            first_name="Sally",
            last_name="Mae",
            customer_type="person",
            creator=self.user,
        )

        # Create a CustomerNote
        self.customer_note = CustomerNote.objects.create(
            note="New note content",
            author=self.user,
            customer= self.customer
        )

        # Create a CustomerNoteHistory instance
        self.note_history = CustomerNoteHistory.objects.create(
            customer_note=self.customer_note,
            previous_note="Previous note content",
            edited_by=self.user,
        )
        

    def test_customer_note_field(self):
        """
            Tests the customer_note field of CustomerNoteHistory.
        """
        self.assertEqual(self.note_history.customer_note, self.customer_note, msg="The customer_note field in the history should be the same as the original CustomerNote note instance.")
    
    def test_previous_note_field(self):
        """
        Tests the previous_note field of CustomerNoteHistory.
        """
        expected_note = "Previous note content" 
        self.assertEqual(
            self.note_history.previous_note, 
            expected_note, 
            msg="The previous_note field saved in the history instance should match the content."
        )
    def test_edited_by_field(self):
        """
            Test the edited_by field of CustomerNoteHistory.
        """
        self.assertEqual(self.note_history.edited_by, self.user, msg="The edited_by field of a note should match the user field assigned to it.")
        
        
    def test_edited_at_field(self):
        """
            Test the edited_at field of CustomerNoteHistory.
        """
        self.assertIsNotNone(self.note_history.edited_at, msg="The edited_at field should not be null as it is added automatically.")
        self.assertIsInstance(self.note_history.edited_at, datetime, msg="The edited_at field should be an instance of datetime")
        
    def test_customer_note_set_null_on_delete(self):
        """
            Tests that customer_note for the note history is set to NULL if the original CustomerNote is deleted.
        """
        self.customer_note.delete()
        self.note_history.refresh_from_db()
        self.assertIsNone(self.note_history.customer_note, msg="The customer_note field is set to NULL if the original CustomerNote is deleted.")
        
    def test_edited_by_set_null_on_delete(self):
        """
            Tests that edited_by field in the note history is set to NULL if the linked CustomUser is deleted.
        """
        self.user.delete()
        self.note_history.refresh_from_db()
        self.assertIsNone(self.note_history.edited_by, msg="The edited_by field should be NULL if the user is deleted.")
        
    def test_str_method(self):
        """
            Tests the __str__ method of CustomerNoteHistory.
        """
        expected_str = f'{self.customer_note} was last edited by {self.user} at {self.note_history.edited_at.strftime("%B %d, %Y, %I:%M %p")}'
        self.assertEqual(str(self.note_history), expected_str, msg="The __str__ method should return the expected string output.")
            
    def test_previous_note_blank(self):
        """
            Tests that previous_note cannot be blank as the original note must contain some characters.
        """
        with self.assertRaises(ValidationError, msg="The previous_note field cannot be blank."):
            note_history = CustomerNoteHistory(
                customer_note=self.customer_note,
                previous_note="",  
                edited_by=self.user,
            )
            note_history.full_clean()
    
    def test_customer_note_null(self):
        """
            Tests that the new customer_note can be NULL.
        """
        note_history = CustomerNoteHistory.objects.create(
            customer_note=None,
            previous_note="Previous note content",
            edited_by=self.user,
        )
        self.assertIsNone(note_history.customer_note, msg="The customer_note field should allow NULL values.")
        
    def test_edited_by_null(self):
        """
            Tests that edited_by can be NULL.
        """
        note_history = CustomerNoteHistory.objects.create(
            customer_note=self.customer_note,
            previous_note="Previous note content",
            edited_by=None,
        )
        self.assertIsNone(note_history.edited_by, msg="The edited_by field should allow NULL values.")
        
class CustomerDocumentHistoryModelTestCase(TestCase):
    def setUp(self):
        """
            Sets up test data for CustomerDocumentHistory.
        """
        # Create a CustomUser
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )
        # create a customer
        self.customer = Customer.objects.create(
            first_name="Sally",
            last_name="Mae",
            customer_type="person",
            creator=self.user,
        )

        # Create a CustomerDocument
        self.document = CustomerDocument.objects.create(
            file="example.pdf",
            file_type="PDF",
            file_detail="Initial document description",
            author=self.user,
            customer = self.customer
        )

        # Create a CustomerDocumentHistory instance
        self.document_history = CustomerDocumentHistory.objects.create(
            document=self.document,
            edited_by=self.user,
            previous_file_name="old_example.pdf",
            previous_file_type="DOC",
            previous_file_detail="Old document description",
        )

    def test_document_field(self):
        """
            Tests the document field of CustomerDocumentHistory.
        """
        self.assertEqual(self.document_history.document, self.document, msg="The document field should match the created CustomerDocument instance.")

    def test_edited_at_field(self):
        """
            Tests the edited_at field of CustomerDocumentHistory.
        """
        self.assertIsNotNone(self.document_history.edited_at, "The edited_at field should not be null.")
        self.assertIsInstance(self.document_history.edited_at, datetime, msg="The edited_at field should be a datetime instance.")

    def test_edited_by_field(self):
        """
            Tests the edited_by field of CustomerDocumentHistory.
        """
        self.assertEqual(self.document_history.edited_by, self.user, msg="The edited_by field should match the created CustomUser instance.")

    def test_previous_file_name_field(self):
        """
            Tests the previous_file_name field of CustomerDocumentHistory.
        """
        self.assertEqual(self.document_history.previous_file_name, "old_example.pdf", msg="The previous_file_name field should store the correct file name.")

    def test_previous_file_type_field(self):
        """
            Tests the previous_file_type field of CustomerDocumentHistory.
        """
        self.assertEqual(self.document_history.previous_file_type, "DOC", msg="The previous_file_type field should store the correct file type.")

    def test_previous_file_detail_field(self):
        """
            Tests the previous_file_detail field of CustomerDocumentHistory.
        """
        self.assertEqual(self.document_history.previous_file_detail, "Old document description", msg="The previous_file_detail field should store the correct description.")

    def test_str_method(self):
        """
            Tests the __str__ method of CustomerDocumentHistory.
        """
        expected_str = f"Edit on {self.document} at {self.document_history.edited_at}"
        self.assertEqual(str(self.document_history), expected_str, msg="The __str__ method should return the correct string representation.")

    def test_save_method_with_empty_file_detail(self):
        """
            Tests the save method when previous_file_detail is empty.
        """
        document_history = CustomerDocumentHistory(
            document=self.document,
            edited_by=self.user,
            previous_file_name="old_example.pdf",
            previous_file_type="DOC",
            previous_file_detail="",  # Empty file detail
        )
        document_history.save()
        self.assertEqual(document_history.previous_file_detail, "No description provided", msg="The save method should set 'No description provided' if previous_file_detail is empty.")

    def test_edited_by_set_null_on_delete(self):
        """
            Tests that edited_by is set to NULL when the referenced CustomUser is deleted.
        """
        self.user.delete()
        self.document_history.refresh_from_db()
        self.assertIsNone(self.document_history.edited_by, msg="The edited_by field should be NULL after the referenced CustomUser is deleted.")

    def test_document_cascade_on_delete(self):
        """
            Tests that the CustomerDocumentHistory instance is deleted when the referenced CustomerDocument is deleted.
        """
        self.document.delete()
        with self.assertRaises(CustomerDocumentHistory.DoesNotExist, msg="The CustomerDocumentHistory instance should be deleted when the referenced CustomerDocument is deleted."):
            self.document_history.refresh_from_db()

    def test_meta_ordering(self):
        """
            Tests the Meta ordering of CustomerDocumentHistory.
        """
        # Create another CustomerDocumentHistory instance
        document_history2 = CustomerDocumentHistory.objects.create(
            document=self.document,
            edited_by=self.user,
            previous_file_name="another_example.pdf",
            previous_file_type="PDF",
            previous_file_detail="Another document description",
        )
        # get all instances ordered by edited_at
        histories = CustomerDocumentHistory.objects.all()
        self.assertEqual(histories[0], document_history2, msg="The instances should be ordered by edited_at in descending order.")