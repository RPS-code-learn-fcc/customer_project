from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.apps import apps

from .models import CustomerMailingList, Customer, Address

@receiver(m2m_changed, sender=CustomerMailingList.interests.through)
def update_customers_and_addresses(sender, instance, action, **kwargs):
    """Updates the mailing list customers and their mailing addresses when interests change.
       Only customers with valid mailing addresses are included in the list."""
    
    if action in ["post_add", "post_remove", "post_clear"]:
        Customer = apps.get_model('customers', 'Customer')
        Address = apps.get_model('customers', 'Address')

        # Get customers who match the selected interests
        customers = Customer.objects.filter(
            interests__in=instance.interests.all(),
            is_inactive=False
        ).distinct()

        # Get only addresses that are valid mailing addresses
        addresses = Address.objects.filter(
            customer_addresses__in=customers,
            mailing_address=True
        ).distinct()

        # Ensure only customers who have at least one valid mailing address are included
        valid_customers = customers.filter(
            addresses__in=addresses,
            is_inactive=False
        ).distinct()

        # Update the mailing list customers
        instance.customers.set(valid_customers)

        # Update the mailing list addresses (assuming the mailing list model has an 'addresses' M2M field)
        instance.addresses.set(addresses)

        # Print statements for debugging
        print(f"Updated Customers in Mailing List: {[c.display_name for c in instance.customers.all()]}")



@receiver(m2m_changed, sender=Customer.interests.through)
def update_customer_mailing_lists(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Automatically add or remove customers from mailing lists when their interests change.
    """
    CustomerMailingList = apps.get_model('customers', 'CustomerMailingList')

    if action == "post_add":
        # When interests are added, find mailing lists matching the added interests
        mailing_lists = CustomerMailingList.objects.filter(interests__in=instance.interests.all()).distinct()
        
        for mailing_list in mailing_lists:
            # Ensure the customer is active and has at least one valid mailing address
            if not instance.is_inactive and instance.addresses.filter(mailing_address=True).exists():
                mailing_list.customers.add(instance)
                print(f"Customer {instance.display_name} added to mailing list: {mailing_list.name}")
            else:
                print(f"ustomer {instance.display_name} NOT added due to inactivity or missing mailing address")

    elif action == "post_remove":
        # When interests are removed, check if the customer still belongs to any relevant mailing list
        mailing_lists = CustomerMailingList.objects.filter(interests__in=pk_set).distinct()

        for mailing_list in mailing_lists:
            # If the customer no longer has any interests in this mailing list, remove them
            remaining_interests = mailing_list.interests.filter(customer_interests=instance)

            # Also ensure the customer is active and has a valid mailing address
            if not remaining_interests.exists() or instance.is_inactive or not instance.addresses.filter(mailing_address=True).exists():
                mailing_list.customers.remove(instance)
                print(f"Customer {instance.display_name} removed from mailing list: {mailing_list.name}")
                
@receiver(post_save, sender=Address)
def update_mailing_list_on_address_change(sender, instance, **kwargs):
    """
    Updates mailing lists when an address is added, modified, or removed.
    Ensures only active customers with at least one valid mailing address are included.
    """
    CustomerMailingList = apps.get_model('customers', 'CustomerMailingList')

    # Get all customers associated with this address
    customers = Customer.objects.filter(addresses=instance)

    for customer in customers:
        if not customer.is_inactive and customer.addresses.filter(mailing_address=True).exists():
            # Add the customer to mailing lists that match their interests
            mailing_lists = CustomerMailingList.objects.filter(interests__in=customer.interests.all()).distinct()
            for mailing_list in mailing_lists:
                mailing_list.customers.add(customer)
            print(f"Customer {customer.display_name} added to mailing lists: {[ml.name for ml in mailing_lists]}")

        else:
            # Remove the customer from mailing lists if they are inactive or no longer have a valid mailing address
            mailing_lists = CustomerMailingList.objects.filter(customers=customer).distinct()
            for mailing_list in mailing_lists:
                mailing_list.customers.remove(customer)
            print(f"Customer {customer.display_name} removed from mailing lists: {[ml.name for ml in mailing_lists]}")