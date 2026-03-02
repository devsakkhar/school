from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser, Role

# Unregister the default Group model as we want to manage it via our Role proxy
admin.site.unregister(Group)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role', 'image')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.site_header = "School Management System"
admin.site.site_title = "School Management System"
admin.site.index_title = "Welcome to School Management System"