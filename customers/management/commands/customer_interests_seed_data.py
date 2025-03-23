from django.core.management.base import BaseCommand
from customers.models import CustomerInterest
from django.core.files import File
import os
from django.conf import settings

class Command(BaseCommand):
    help = "Seeds the database with 8 customer interests and associates icon images from static files."

    def handle(self, *args, **options):
        self.stdout.write("Seeding customer interests...")

        # List of interests to seed
        interests_data = [
            {"name": "Tree Sale", "slug": "tree-sale", "icon": "images/icons/tree.svg"},
            {"name": "Soil Tests", "slug": "soil-tests", "icon": "images/icons/soil.svg"},
            {"name": "Cover Crops", "slug": "cover-crops", "icon": "images/icons/crop.svg"},
            {"name": "LOTL", "slug": "ladies-of-the-land", "icon": "images/icons/lotl-icon.svg"},
            {"name": "Manure Tests", "slug": "manure-tests"},  # No icon provided
            {"name": "Summer Camp", "slug": "summer-camp", "icon": "images/icons/summercamp.svg"},
            {"name": "Rain Barrel Workshop", "slug": "rain-barrels", "icon": "images/icons/rainbarrel.svg"},
            {"name": "Annual Meeting", "slug": "annual-meeting", "icon": "images/icons/annualmeeting.svg"},
        ]

        # Create and save interests
        for interest_data in interests_data:
            # Check if the interest already exists
            interest, created = CustomerInterest.objects.get_or_create(
                name=interest_data["name"],
                slug=interest_data["slug"],
            )

            # Associate the icon image from static files (if provided)
            if "icon" in interest_data:  # Check if the icon key exists
                icon_path = os.path.join(settings.STATIC_ROOT, interest_data["icon"])
                if os.path.exists(icon_path):
                    with open(icon_path, "rb") as f:
                        interest.icon_image.save(os.path.basename(icon_path), File(f))
                    self.stdout.write(self.style.SUCCESS(f"Added icon for {interest.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Icon not found for {interest.name} at {icon_path}"))
            else:
                self.stdout.write(self.style.WARNING(f"No icon provided for {interest.name}"))

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created interest: {interest.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Interest already exists: {interest.name}"))

        self.stdout.write(self.style.SUCCESS("Customer interests seeded successfully!"))