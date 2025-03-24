from django.core.management.base import BaseCommand
from customers.models import Customer, ContactMethod, CustomerInterest, Address, Phone, Email, CustomerNote, CustomerDocument
from app_users.models import CustomUser
from django.contrib.auth.hashers import make_password
from faker import Faker
import random
import re
import os
from django.utils import timezone
from django.core.files import File
from django.conf import settings

class Command(BaseCommand):
    help = "Seeds the database with 100 customers: customer addresses, phones, emails, notes, and documents are all included."

    def handle(self, *args, **options):
        self.stdout.write("Adding customers to db...")

        # create Faker instance
        fake = Faker()

        # user profile data
        users_data = [
            {
                "email": "user1@company.com",
                "password": "user1password123",
                "first_name": "Tanner",
                "last_name": "Boeing",
                "bio": "Passionate about Forestry and logistics",
                "job_title": "District Administrator",
            },
            {
                "email": "user2@company.com",
                "password": "user2password123",
                "first_name": "Kendra",
                "last_name": "Gertz",
                "bio": "Loves Watersheds and Milkweed.",
                "job_title": "Watershed Coordinator",
            },
            {
                "email": "user3@company.com",
                "password": "user3password123",
                "first_name": "Debra",
                "last_name": "Sheetz",
                "bio": "Excited to write engineering plans and organize women in ag/conservation events.",
                "job_title": "Conservation Specialist",
            },
            {
                "email": "user4@company.com",
                "password": "user4password123",
                "first_name": "Joe",
                "last_name": "Cannon",
                "bio": "Dedicated to helping farmers reach their conservation goals.",
                "job_title": "Program Specialist",
            },
        ]

        # create users (if python manage.py app_users_seed_data has not been ran)
        users = [] # create empty users list
        for user_data in users_data:
            user, created = CustomUser.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "password": make_password(user_data["password"]),
                    "bio": user_data["bio"],
                    "job_title": user_data["job_title"],
                },
            )
            
            # add user to users
            users.append(user)
            
            # print information to terminal to show if the user is created or already exists
            if created:
                self.stdout.write(self.style.SUCCESS(f"New user created: {user.email}"))
            else:
                self.stdout.write(self.style.WARNING(f"{user.email} already exists in db"))

        # get allowed customer choices (person, business, organization, government)
        CUSTOMER_TYPES = [choice[0] for choice in Customer.CUSTOMER_CHOICES]

        # get the contact methods that already exist in the db via the command: python manage.py customer_contact_methods_seed_data
        contact_methods = list(ContactMethod.objects.all())
        
        # if this management command has not been run
        if not contact_methods:
            self.stdout.write(self.style.ERROR("Add contanct methods to db first - manually or via comman: python manage.py customer_contact_methods_seed_data")) # error
            return

        # get the interests that already exist in the db via the command:python manage.py customer_interests_seed_data    
        interests = list(CustomerInterest.objects.all())
        if not interests:
            self.stdout.write(self.style.ERROR("Add interests first - manually or via command: python manage.py customer_interests_seed_data"))
            return

        # This is the path to add the document template
        template_pdf_path = os.path.join(settings.STATIC_ROOT, "documents", "template.pdf")
        if not os.path.exists(template_pdf_path):
            self.stdout.write(self.style.ERROR(f"Template PDF not found: {template_pdf_path}. Add template doc to the statif folder."))
            return

        # Create 100 customers with different users as their creators
        for i in range(100):
            # get a creator
            creator = users[i % len(users)]

            # get a random cust. type
            customer_type = random.choice(CUSTOMER_TYPES)

            # use customer_type to determine the type of customer profile to create
            if customer_type == "person":
                first_name = fake.first_name()
                last_name = fake.last_name()
            else:
                first_name = fake.company()
                last_name = ""  # non-person entities have no last name

            # Make the first 10 customers inactive
            is_inactive = i < 10 

            # create new customer instances
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                customer_type=customer_type,
                creator=creator,
                is_inactive=is_inactive,
            )

            # Each customer will have between 0 and 3 preffered contact methods
            customer.preferred_contact_methods.set(random.sample(contact_methods, k=random.randint(0, 3)))

            # each customer will have between 0 and 5 random interests
            customer.interests.set(random.sample(interests, k=random.randint(0, 5)))

            # Aeach customer will have between 0 and 3 addresses
            for _ in range(random.randint(2, 3)):
                address = Address.objects.create(
                    street=fake.street_address(),
                    city=fake.city(),
                    state=fake.state_abbr(),
                    zip_code=fake.zipcode(),
                    mailing_address=random.choice([True, False]),
                )
                customer.addresses.add(address)

            # each customer will have between 0 and 2 phone numbers
            for _ in range(random.randint(0, 2)):
                # create a phone number and an phone extension
                phone_number_with_extension = fake.phone_number()
                phone_number, extension = self._normalize_phone_number(phone_number_with_extension)

                # create a new phone number
                phone = Phone.objects.create(
                    phone_number=phone_number,
                    extension=extension,
                    phone_type=random.choice(["home", "work", "cell", "farm"]),
                    is_primary=random.choice([True, False]),
                    can_call=random.choice([True, False]),
                    can_text=random.choice([True, False]),
                    can_leave_voicemail=random.choice([True, False]),
                )
                # add the phone number to the correct customer instance
                customer.phones.add(phone)

            # Add multiple emails (0 to 2 per customer)
            for _ in range(random.randint(0, 2)):
                email = Email.objects.create(
                    email_address=fake.email(),
                    email_type=random.choice(["home", "work", "farm"]),
                    preferred_email=random.choice([True, False]),
                )
                
                # add the email to the correct customer instance
                customer.emails.add(email)

            # create between 0 and 8 notes for every customer
            num_notes = random.randint(0, 8)  
            for _ in range(num_notes):
                # use faker to create a note
                note = CustomerNote.objects.create(
                    note=fake.paragraph(nb_sentences=5),  
                    author=random.choice(users),  
                    customer=customer,
                )
                
                # to the terminal show that the note was successfully created
                self.stdout.write(self.style.SUCCESS(f"Added note to customer: {customer.display_name}"))

            # associate between 0 to 5 documents with a customer
            num_documents = random.randint(0, 5) 
            for _ in range(num_documents):
                # Randomly select a file type
                file_type = random.choice([choice[0] for choice in CustomerDocument.FILE_TYPES])

                # rename the file in a way that is consisent with the custom save method in the name
                file_name = f"{customer.display_name}_{file_type}_{timezone.now().year}.pdf"

                # keep the length within the character limits:
                file_name = file_name[:100]
                # Open the template PDF file
                with open(template_pdf_path, "rb") as f:
                    # create a new document
                    document = CustomerDocument.objects.create(
                        file=File(f, name=file_name), 
                        file_type=file_type,
                        file_detail=fake.sentence() if file_type == "other" else "",  # Add a file detail if file_type is 'other'
                        author=random.choice(users),  
                        customer=customer,  
                    )
                    
                    # show in terminal that a document was succesffully added
                    self.stdout.write(self.style.SUCCESS(f"Added document to customer: {customer.display_name}"))

            # terminal message showing whether a customer is inactive or not
            status = "Inactive" if is_inactive else "Active"
            self.stdout.write(self.style.SUCCESS(f"Created {status} customer: {customer.display_name} (Created by: {creator.email})"))

        self.stdout.write(self.style.SUCCESS("Customers seeded successfully!"))

    def _normalize_phone_number(self, phone_number_with_extension):
        """
        Faker may create a phone number that does not match the validation in the Phone model. Normalize the phone numbers so that:
        - It is 10 digits long (USA phone #)
        - an extesion is separately extracted
        - there are only digits - no 'x' for extension, etc.
        """
        # Remove all non-digit characters
        phone_number_with_extension = re.sub(r"[^0-9x]", "", phone_number_with_extension)

        # if an extension is created by faker, separate it from the phone number
        if "x" in phone_number_with_extension:
            phone_number, extension = phone_number_with_extension.split("x", 1)
        else:
            phone_number, extension = phone_number_with_extension, ""

        # phone number should be 10 digits exactly to match a USA based phone number style
        if len(phone_number) > 10:
            phone_number = phone_number[:10]  
        elif len(phone_number) < 10:
            phone_number = phone_number.ljust(10, "0") 

        return phone_number, extension