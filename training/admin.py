from django.contrib import admin

from .models import Category, Region, TrainingProgram


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "category", "duration_weeks", "is_active", "created_at")
    list_filter = ("is_active", "region", "category")
    search_fields = ("title", "description")
    list_editable = ("is_active",)
    date_hierarchy = "created_at"
