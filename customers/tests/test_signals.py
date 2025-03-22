from django.test import TestCase
from django.db.models.signals import m2m_changed
from customers.models import Customer, Address, CustomerMailingList, CustomerInterest
from customers.signals import update_customers_and_addresses, update_customer_mailing_lists, update_mailing_list_on_address_change
from app_users.models import CustomUser
from django.db.models.signals import post_save

class CustomerMailingListSignalTests(TestCase):
    def setUp(self):
        # create a user
        self.user = CustomUser.objects.create_user(
            email="test@test.com",
            password="testpassword123",
        )
        self.client.login(email="test@test.com", password="testpassword123")

        # Connect the signal for testing
        m2m_changed.connect(update_customers_and_addresses, sender=CustomerMailingList.interests.through)

        # Create test data
        self.interest1 = CustomerInterest.objects.create(name="Interest 1", slug="interest-1")
        self.interest2 = CustomerInterest.objects.create(name="Interest 2", slug="interest-2")

        self.customer1 = Customer.objects.create(first_name="Customer 1", customer_type="person", is_inactive=False)
        self.customer2 = Customer.objects.create(first_name="Customer 2", customer_type="person", is_inactive=False)

        self.address1 = Address.objects.create(street="222 Washington St", city="Jacksonville", state="NY", zip_code="56743", mailing_address=True)
        self.address2 = Address.objects.create(street="233 Washington St", city="Milton", state="HI", zip_code="99999", mailing_address=False)

        self.customer1.addresses.add(self.address1)
        self.customer2.addresses.add(self.address2)
        
        self.customer1.interests.add(self.interest1)
        self.customer2.interests.add(self.interest2)

        self.mailing_list = CustomerMailingList.objects.create(name="Mailing List 1")
   

    def tearDown(self):
        # Disconnect the signal after testing
        m2m_changed.disconnect(update_customers_and_addresses, sender=CustomerMailingList.interests.through)

    def test_update_customers_and_addresses_on_post_add(self):
        # Add interests to the mailing list
        self.mailing_list.interests.add(self.interest1, self.interest2)

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customers and addresses are updated correctly
        self.assertIn(self.customer1, self.mailing_list.customers.all()) # only customers with valid interests and a mailing address are added
        self.assertNotIn(self.customer2, self.mailing_list.customers.all())  # Customer 2 has no valid mailing address
        
        # Change self.address2.mailing_address to True
        self.address2.mailing_address = True
        self.address2.save()

        # Refresh the mailing list instance to reflect the changes
        self.mailing_list.refresh_from_db()

        # makes sure that Customer 2 is now included in the mailing list
        self.assertIn(self.customer2, self.mailing_list.customers.all())  # Customer 2 now has a valid mailing address
        
        # makes sure that there are now two customers in the mailing list
        self.assertEqual(len(self.mailing_list.customers.all()), 2)  # Both customers should now be in the mailing list

    def test_update_customers_and_addresses_on_post_remove(self):
        # Add interests to the mailing list
        self.mailing_list.interests.add(self.interest1, self.interest2)

        # Remove one interest
        self.mailing_list.interests.remove(self.interest1)

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customers and addresses are updated correctly
        self.assertNotIn(self.customer1, self.mailing_list.customers.all())  # Customer 1 is no longer associated
        self.assertNotIn(self.customer2, self.mailing_list.customers.all())

    def test_update_customers_and_addresses_on_post_clear(self):
            """
            Test that customers and addresses are updated correctly when all interests are cleared from the mailing list.
            """
            # Add interests to the mailing list
            self.mailing_list.interests.add(self.interest1, self.interest2)

            # Clear all interests
            self.mailing_list.interests.clear()

            # Refresh the mailing list instance
            self.mailing_list.refresh_from_db()

            # makes sure that the customers and addresses are updated correctly
            self.assertEqual(self.mailing_list.customers.count(), 0)  # No customers should be associated
            self.assertEqual(self.mailing_list.addresses.count(), 0)  # No addresses should be associated
            
    def test_update_customers_and_addresses_with_inactive_customer(self):
            """
            Test that inactive customers are not added to the mailing list.
            """
            # Mark customer1 as inactive
            self.customer1.is_inactive = True
            self.customer1.save()

            # Add interests to the mailing list
            self.mailing_list.interests.add(self.interest1, self.interest2)

            # Refresh the mailing list instance
            self.mailing_list.refresh_from_db()

            # makes sure that inactive customers are not added
            self.assertNotIn(self.customer1, self.mailing_list.customers.all())
            self.assertNotIn(self.customer2, self.mailing_list.customers.all())  # Customer 2 has no valid mailing address

    def test_update_customers_and_addresses_with_no_valid_addresses(self):
        """
        Test that customers without valid mailing addresses are not added to the mailing list.
        """
        # Remove valid mailing address from customer1
        self.address1.mailing_address = False
        self.address1.save()

        # Add interests to the mailing list
        self.mailing_list.interests.add(self.interest1, self.interest2)

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that customers without valid mailing addresses are not added
        self.assertNotIn(self.customer1, self.mailing_list.customers.all())
        self.assertNotIn(self.customer2, self.mailing_list.customers.all())  # Customer 2 has no valid mailing address
        
class UpdateCustomerMailingListsSignalTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create_user(
            email="test@test.com",
            password="testpassword123",
        )
        self.client.login(email="test@test.com", password="testpassword123")

        # Connect the signal for testing
        m2m_changed.connect(update_customer_mailing_lists, sender=Customer.interests.through)

        # Create test data
        self.interest1 = CustomerInterest.objects.create(name="Interest 1", slug="interest-1")
        self.interest2 = CustomerInterest.objects.create(name="Interest 2", slug="interest-2")

        self.customer1 = Customer.objects.create(first_name="Customer 1", customer_type="person", is_inactive=False)
        self.customer2 = Customer.objects.create(first_name="Customer 2", customer_type="person", is_inactive=False)

        self.address1 = Address.objects.create(street="222 Washington St", city="Jacksonville", state="NY", zip_code="56743", mailing_address=True)
        self.address2 = Address.objects.create(street="233 Washington St", city="Milton", state="HI", zip_code="99999", mailing_address=False)

        self.customer1.addresses.add(self.address1)
        self.customer2.addresses.add(self.address2)

        self.mailing_list = CustomerMailingList.objects.create(name="Mailing List 1")
        self.mailing_list.interests.add(self.interest1, self.interest2)  # Link interests to the mailing list
        
        self.customer1.interests.add(self.interest1)
        self.customer2.interests.add(self.interest2)

    def tearDown(self):
        # Disconnect the signal after testing
        m2m_changed.disconnect(update_customer_mailing_lists, sender=Customer.interests.through)

    def test_add_customer_to_mailing_list_on_interest_add(self):
        """
        Test that a customer is added to a mailing list when their interests match the mailing list's interests.
        """

        # makes sure that the customer is added to the mailing list
        self.assertIn(self.customer1, self.mailing_list.customers.all())

    def test_remove_customer_from_mailing_list_on_interest_remove(self):
        """
        Test that a customer is removed from a mailing list when their interests no longer match.
        """
        # Add the customer to the mailing list initially
        self.mailing_list.customers.add(self.customer1)

        # makes sure initial state
        self.assertIn(self.customer1, self.mailing_list.customers.all())

        # Remove the interest from the customer
        self.customer1.interests.remove(self.interest1)

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customer is removed from the mailing list
        self.assertNotIn(self.customer1, self.mailing_list.customers.all())

    def test_customer_without_mailing_address_not_added_to_mailing_list(self):
        """
        Test that a customer without a valid mailing address is not added to a mailing list.
        """
        # Remove the valid mailing address from the customer
        self.address1.mailing_address = False
        self.address1.save()

        # Add an interest to the customer that matches the mailing list
        self.customer1.interests.add(self.interest1)

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customer is not added to the mailing list
        self.assertNotIn(self.customer1, self.mailing_list.customers.all())

    def test_customer_removed_from_mailing_list_when_mailing_address_invalid(self):
        """
        Test that a customer is removed from a mailing list if their mailing address becomes invalid.
        """
        # Add the customer to the mailing list initially
        self.mailing_list.customers.add(self.customer1)

        # makes sure initial state
        self.assertIn(self.customer1, self.mailing_list.customers.all())

        # Remove the valid mailing address from the customer
        self.address1.mailing_address = False
        self.address1.save()

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customer is removed from the mailing list
        self.assertNotIn(self.customer1, self.mailing_list.customers.all())
        

class UpdateMailingListOnAddressChangeSignalTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create_user(
            email="test@test.com",
            password="testpassword123",
        )
        self.client.login(email="test@test.com", password="testpassword123")

        # Connect the signal for testing
        post_save.connect(update_mailing_list_on_address_change, sender=Address)

        # Create test data
        self.interest1 = CustomerInterest.objects.create(name="Interest 1", slug="interest-1")
        self.interest2 = CustomerInterest.objects.create(name="Interest 2", slug="interest-2")

        self.customer1 = Customer.objects.create(first_name="Customer 1", customer_type="person", is_inactive=False)
        self.customer2 = Customer.objects.create(first_name="Customer 2", customer_type="person", is_inactive=False)

        self.address1 = Address.objects.create(street="222 Washington St", city="Jacksonville", state="NY", zip_code="56743", mailing_address=True)
        self.address2 = Address.objects.create(street="233 Washington St", city="Milton", state="HI", zip_code="99999", mailing_address=False)

        self.customer1.addresses.add(self.address1)
        self.customer2.addresses.add(self.address2)
        
        self.customer1.interests.add(self.interest1)
        self.customer2.interests.add(self.interest2)

        self.mailing_list = CustomerMailingList.objects.create(name="Mailing List 1")
        self.mailing_list.interests.add(self.interest1, self.interest2)

    def tearDown(self):
        # Disconnect the signal after testing
        post_save.disconnect(update_mailing_list_on_address_change, sender=Address)

    def test_add_customer_to_mailing_list_on_valid_address(self):
        """
        Test that a customer is added to a mailing list when they have a valid mailing address.
        """
   
        # Update the address to be valid (if not already)
        self.address1.mailing_address = True
        self.address1.save()

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customer is added to the mailing list
        self.assertIn(self.customer1, self.mailing_list.customers.all())

    def test_remove_customer_from_mailing_list_on_invalid_address(self):
        """
        Test that a customer is removed from a mailing list when their mailing address becomes invalid.
        """
        # Add the customer to the mailing list initially
        self.mailing_list.customers.add(self.customer1)

        # makes sure initial state
        self.assertIn(self.customer1, self.mailing_list.customers.all())

        # Update the address to be invalid
        self.address1.mailing_address = False
        self.address1.save()

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customer is removed from the mailing list
        self.assertNotIn(self.customer1, self.mailing_list.customers.all())

    def test_inactive_customer_not_added_to_mailing_list(self):
        """
        Test that an inactive customer is not added to a mailing list, even if they have a valid mailing address.
        """
        # Mark the customer as inactive
        self.customer1.is_inactive = True
        self.customer1.save()

        # Update the address to be valid
        self.address1.mailing_address = True
        self.address1.save()

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customer is not added to the mailing list
        self.assertNotIn(self.customer1, self.mailing_list.customers.all())

    def test_customer_without_mailing_address_not_added_to_mailing_list(self):
        """
        Test that a customer without a valid mailing address is not added to a mailing list.
        """
        # checks the address is invalid
        self.address1.mailing_address = False
        self.address1.save()

        # Refresh the mailing list instance
        self.mailing_list.refresh_from_db()

        # makes sure that the customer is not added to the mailing list
        self.assertNotIn(self.customer1, self.mailing_list.customers.all())