from django.core.management.base import BaseCommand
from app_users.models import CustomUser
from django.contrib.auth.hashers import make_password  # To hash passwords

class Command(BaseCommand):
    help = "Seeds the production PostgreSQL database with user data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding user data for app_users...")

        # List of users to seed
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

        # Create and save users
        for user_data in users_data:
            user = CustomUser.objects.create(
                email=user_data["email"],
                password=make_password(user_data["password"]),  # Hash the password
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                bio=user_data["bio"],
                job_title=user_data["job_title"],
            )
            self.stdout.write(self.style.SUCCESS(f"Created user: {user.email}"))

        self.stdout.write(self.style.SUCCESS("User data seeded successfully!"))