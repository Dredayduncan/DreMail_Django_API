from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(EmailGroup)
admin.site.register(Email)
admin.site.register(EmailTransfer)
admin.site.register(Favorites)
admin.site.register(Junk)
admin.site.register(Trash)
admin.site.register(Spam)
admin.site.register(Drafts)


