from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["email", "username", "tier", "is_premium", "is_staff"]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("tier", "is_premium")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("email", "tier", "is_premium")}),
    )
