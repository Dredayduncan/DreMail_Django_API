from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(EmailUser)
admin.site.register(EmailGroup)
admin.site.register(UserEmailGroup)
admin.site.register(Email)
admin.site.register(EmailTransfer)
admin.site.register(Favorites)
admin.site.register(Junk)
admin.site.register(DeletedEmail)
admin.site.register(Spam)
admin.site.register(Drafts)


