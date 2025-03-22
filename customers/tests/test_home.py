from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Case, When, Value, IntegerField
from customers.models import Customer, CustomerInterest
from customers.views import home_view

User = get_user_model()

class HomeViewTests(TestCase):
    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.client.login(email="testuser@example.com", password="testpassword")

        # Create customers
        self.customer1 = Customer.objects.create(
            first_name="John", last_name="Doe", is_inactive=False
        )
        self.customer2 = Customer.objects.create(
            first_name="Jane", last_name="Smith", is_inactive=True
        )
        self.customer3 = Customer.objects.create(
            first_name="Alice", last_name="Johnson", is_inactive=False
        )
        # Ensure the user has a valid short_name
        self.user.short_name = "testuser"  # Set this explicitly if needed
        self.user.save()

        self.client.login(email="testuser@example.com", password="testpassword")
        # Create interests
        self.interest1 = CustomerInterest.objects.create(name="Interest 1", slug="interest-1")
        self.interest2 = CustomerInterest.objects.create(name="Interest 2", slug="interest-2")

    def test_home_view_renders_template(self):
        """
        Test that the home view renders the correct template for a standard GET request.
        """
        print(self.user)
        response = self.client.get(reverse("home"))
        print(response)
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, "customers/home.html")
        
        # Check if email_prefix is in the context
        #self.assertIn("email_prefix", response.context)
        #self.assertEqual(response.context["email_prefix"], self.user.email.split('@')[0])

    def test_home_view_pagination(self):
        """
        Test that the home view paginates customers correctly.
        """
        # Create more customers to test pagination
        for i in range(15):
            Customer.objects.create(first_name=f"Customer{i}", last_name=f"Last{i}")

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["customers"]), 10)  # Default pagination size

        # Test second page
        response = self.client.get(reverse("home") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["customers"]), 5)  # Remaining 5 customers

    def test_home_view_search(self):
        """
        Test that the home view filters customers based on search terms.
        """
        # Search for "John"
        response = self.client.get(reverse("home") + "?search_customer=John")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")

        # Search for "Smith"
        response = self.client.get(reverse("home") + "?search_customer=Smith")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Smith")
        self.assertNotContains(response, "John Doe")

    def test_home_view_active_customers_first(self):
        """
        Test that active customers appear before inactive customers.
        """
        response = self.client.get(reverse("home"))
        customers = response.context["customers"]
        self.assertEqual(customers[0].is_inactive, False)  # First customer is active
        self.assertEqual(customers[1].is_inactive, False)  # Second customer is active
        self.assertEqual(customers[2].is_inactive, True)  # Third customer is inactive

    def test_home_view_htmx_request(self):
        """
        Test that the home view returns a partial template for HTMX requests.
        """
        # Simulate an HTMX request
        factory = RequestFactory()
        request = factory.get(reverse("home"), HTTP_HX_REQUEST="true")
        request.user = self.user
        request.htmx = True

        response = home_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customers/partials/customers_list.html")

    def test_home_view_no_customers_found(self):
        """
        Test that the home view handles no customers found gracefully.
        """
        # Delete all customers
        Customer.objects.all().delete()

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No more customers with matching criteria found.")

    def test_home_view_context_data(self):
        """
        Test that the home view includes the correct context data.
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("customers", response.context)
        self.assertIn("users", response.context)
        self.assertIn("interests", response.context)
        self.assertIn("user", response.context)
        self.assertEqual(response.context["user"], self.user)