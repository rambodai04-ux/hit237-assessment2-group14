from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    CONSTRUCTION = "construction"
    CARE = "care"
    LAND_MANAGEMENT = "land_management"
    TOURISM = "tourism"

    CATEGORY_CHOICES = [
        (CONSTRUCTION, "Construction"),
        (CARE, "Care"),
        (LAND_MANAGEMENT, "Land Management"),
        (TOURISM, "Tourism"),
    ]

    name = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        unique=True,
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.get_name_display()


class TrainingProgram(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_weeks = models.PositiveIntegerField()
    eligibility = models.TextField()
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="programs",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="programs",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    # --- Fat model classmethods ---

    @classmethod
    def get_active_programs(cls):
        """Return all currently active training programs."""
        return cls.objects.filter(is_active=True).select_related("region", "category")

    @classmethod
    def get_programs_by_region(cls, region_id):
        """Return active programs for a given region."""
        return cls.get_active_programs().filter(region_id=region_id)

    @classmethod
    def get_programs_by_category(cls, category_id):
        """Return active programs for a given category."""
        return cls.get_active_programs().filter(category_id=category_id)

    # --- Fat model instance method ---

    def get_summary(self):
        """Return a short human-readable summary of this program."""
        return (
            f"{self.title} — {self.region.name} | "
            f"{self.category.get_name_display()} | "
            f"{self.duration_weeks} week{'s' if self.duration_weeks != 1 else ''}"
        )
