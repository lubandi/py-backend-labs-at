from django.contrib import admin

from .models import URL, Click, Tag


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ["short_code", "original_url", "owner", "click_count", "created_at"]
    list_filter = ["created_at", "is_active"]
    search_fields = ["short_code", "original_url", "title"]
    readonly_fields = ["click_count"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ["url", "clicked_at", "ip_address", "country"]
    list_filter = ["clicked_at", "country"]
