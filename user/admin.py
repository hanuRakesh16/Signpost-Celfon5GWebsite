from django.contrib import admin
from user.models import *
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

# Register your models here.
admin.site.site_header = "Signpost Celfon Admin Panel"
admin.site.site_title = "Signpost Celfon Admin Panel"
admin.site.index_title = "Welcome to Signpost Celfon Admin Panel"

class UserAdmin(admin.ModelAdmin):
    list_display = ("role", "description")


admin.site.register(Careers)
admin.site.register(Creditvalues)
admin.site.register(Transaction)
admin.site.register(FaqSub)
admin.site.register(Faqs)