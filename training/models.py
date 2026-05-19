from django.db import models
from django.db.models import Count, Q, Prefetch 
from django.utils.text import slugify


class Region(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    @classmethod
    def with_programs(cls):
        return cls.objects.prefetch_related("programs")

    @classmethod
    def with_program_counts(cls):
        return (
            cls.objects
            .annotate(
                program_count=Count("programs"),               
                active_program_count=Count(                    
                    "programs",
                    filter=Q(programs__is_active=True)
                ),
            )
            .order_by("name")
        )




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
    
    @classmethod
    def with_program_counts(cls):
        return (
            cls.objects
            .annotate(
                program_count=Count("programs"),               
                active_program_count=Count(                    
                    "programs",
                    filter=Q(programs__is_active=True)
                ),
            )
            .order_by("-active_program_count")                
        )



class TrainingProgram(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)  
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
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # --- Fat model classmethods ---

    @classmethod
    def get_active_programs(cls):
      
        return (
            cls.objects
            .filter(is_active=True)
            .select_related("region", "category")       
        )

    @classmethod
    def get_programs_by_region(cls, region_id):
        """Return active programs for a given region."""
        return cls.get_active_programs().filter(region_id=region_id)

    @classmethod
    def get_programs_by_category(cls, category_id):
        """Return active programs for a given category."""
        return cls.get_active_programs().filter(category_id=category_id)
    
    @classmethod
    def get_programs_by_category_name(cls, category_name):
        """
        Task 1.2.3 — filter across FK relationship using __ syntax.
        e.g. category_name="construction"
        """
        return (
            cls.get_active_programs()
            .filter(category__name=category_name)             
        )

    @classmethod
    def get_programs_by_region_name(cls, region_name):
        """Task 1.2.3 — __ traversal + icontains across FK."""
        return (
            cls.get_active_programs()
            .filter(region__name__icontains=region_name)       
        )

    @classmethod
    def get_long_programs(cls, min_weeks=8):
        """
        Task 1.2.1 — filter with __gte comparison lookup, ordered.
        """
        return (
            cls.get_active_programs()
            .filter(duration_weeks__gte=min_weeks)           
            .order_by("duration_weeks")
        )

    @classmethod
    def count_by_category(cls):
        """
        Task 1.4.1 — annotate Category with program count,
        filter on annotation (num_programs__gte=1), order descending.
        """
        return (
            Category.objects
            .annotate(num_programs=Count("programs"))         
            .filter(num_programs__gte=1)                       
            .order_by("-num_programs")                        
        )

    @classmethod
    def with_region_programs(cls):
        """
        Task 1.3.3 — prefetch reverse FK (programs on each region).
        Task 1.4.2 — filtered Count annotation on each region.

        Returns Region queryset, not TrainingProgram.
        Used in views that iterate regions and show their programs.
        2 queries total instead of N+1.
        """
        return (
            Region.objects
            .prefetch_related(
                Prefetch(
                    "programs",
                    queryset=cls.objects
                             .filter(is_active=True)
                             .select_related("category")       
                             .order_by("-created_at"),
                )
            )
            .annotate(
                active_program_count=Count(                   
                    "programs",
                    filter=Q(programs__is_active=True)
                )
            )
        )


    # --- Fat model instance method ---

    def get_summary(self):
        """Return a short human-readable summary of this program."""
        weeks = self.duration_weeks
        return (
            f"{self.title} — {self.region.name} | "
            f"{self.category.get_name_display()} | "
            f"{self.duration_weeks} week{'s' if self.duration_weeks != 1 else ''}"
        )
    

    @property
    def is_long_program(self):
        """True if program runs longer than 8 weeks — encapsulated rule."""
        return self.duration_weeks > 8

    @property
    def duration_display(self):
        """Formatted duration string — DRY, reusable in templates."""
        w = self.duration_weeks
        return f"{w} week{'s' if w != 1 else ''}"
