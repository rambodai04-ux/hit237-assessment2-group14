from django.contrib import admin
from django.db.models import Count
from .models import Category, Region, TrainingProgram


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display  = ("name", "slug", "program_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _program_count=Count("programs")
        )
    
    @admin.display(description="Programs", ordering="_program_count")
    def program_count(self, obj):
        return obj._program_count

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ("name", "get_name_display", "active_program_count")
    search_fields = ("name",)

    def get_queryset(self, request):
            from django.db.models import Q
            return super().get_queryset(request).annotate(
                _active_count=Count(
                    "programs",
                    filter=Q(programs__is_active=True)
                )
            )
    @admin.display(description="Active Programs", ordering="_active_count")
    def active_program_count(self, obj):
        return obj._active_count



@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "category", "duration_weeks", "is_active", "is_long_program_display","created_at")
    list_filter = ("is_active", "region", "category")
    search_fields = ("title", "description")
    list_editable = ("is_active",)
    date_hierarchy = "created_at"
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "get_summary_display")


    list_select_related = ("region", "category")

    fieldsets = (
        ("Program Info", {
            "fields": ("title", "slug", "description", "eligibility")
        }),
        ("Classification", {
            "fields": ("region", "category", "duration_weeks")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Read-only", {
            "fields": ("created_at", "updated_at", "get_summary_display"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Long Program (>8wks)", boolean=True)
    def is_long_program_display(self, obj):
        # Calls the model property — DRY
        return obj.is_long_program

    @admin.display(description="Summary")
    def get_summary_display(self, obj):
        # Calls the model instance method — DRY
        return obj.get_summary()
