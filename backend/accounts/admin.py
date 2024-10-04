from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


class CustomerUserAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'activity', 'phone_number', 'is_active', 'is_staff')
    ordering = ('date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(User, CustomerUserAdmin)