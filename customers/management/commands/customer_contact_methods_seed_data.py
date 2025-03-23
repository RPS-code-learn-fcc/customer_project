from django.core.management.base import BaseCommand
from customers.models import ContactMethod

class Command(BaseCommand):
    help = "Seeds the database with preferred contact methods."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Customer contact methods...")

        # List of contact methods to seed
        contact_methods_data = [
            {"method_name": "Phone"},
            {"method_name": "Email"},
            {"method_name": "Text"},
            {"method_name": "Voicemail"},
            {"method_name": "Mail"},
        ]

        # Create and save contact methods
        for method_data in contact_methods_data:
            # Check if the contact method already exists
            method, created = ContactMethod.objects.get_or_create(
                method_name=method_data["method_name"],
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created contact method: {method.method_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Contact method already exists: {method.method_name}"))

        self.stdout.write(self.style.SUCCESS("Contact methods seeded successfully!"))