from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

# Customize admin site titles
admin.site.site_header = "Administration"
admin.site.site_title = "Admin"
admin.site.index_title = "FreeCups"

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    min_num = 0
    max_num = 1
    extra = 0

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    ordering = ("email",)
    list_display = ("email", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "groups")
    search_fields = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "is_staff", "is_active")}),
    )
    
    def delete_model(self, request, obj):
        """Delete user and related profile without permission check"""
        obj.delete()
    
    def delete_queryset(self, request, queryset):
        """Bulk delete users without permission check"""
        queryset.delete()

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "is_buyer", "is_holder")
    list_filter = ("is_buyer", "is_holder")
    search_fields = ("user__email", "first_name", "last_name")
    
    def delete_queryset(self, request, queryset):
        """Bulk delete: call delete() on each profile to trigger model logic"""
        for profile in queryset:
            profile.delete()
