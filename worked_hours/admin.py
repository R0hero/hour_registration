from django.contrib import admin

from .models import Company, Project, Timecard

# Register your models here.
admin.site.register(Company)
admin.site.register(Project)
admin.site.register(Timecard)