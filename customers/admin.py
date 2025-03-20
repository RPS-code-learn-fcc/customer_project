from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Customer)
admin.site.register(CustomerRelationship)

admin.site.register(Address)
admin.site.register(Email)
admin.site.register(Phone)
admin.site.register(ContactMethod)

admin.site.register(CustomerDocument)
admin.site.register(CustomerNote)
admin.site.register(CustomerNoteHistory)
admin.site.register(CustomerDocumentHistory)

admin.site.register(CustomerInterest)
admin.site.register(CustomerMailingList)


