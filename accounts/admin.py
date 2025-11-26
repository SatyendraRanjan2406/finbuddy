from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import PhoneOTP, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "phone", "email", "first_name", "last_name", "is_staff", "date_joined")
    search_fields = ("username", "phone", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("phone",)}),
    )


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "otp_code", "is_verified", "created_at")
    search_fields = ("phone_number",)
    list_filter = ("is_verified", "created_at")
    readonly_fields = ("created_at", "updated_at")
