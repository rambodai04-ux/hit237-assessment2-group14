from django.views.generic import DetailView, ListView
from django.db.models import Q, Prefetch, Count
from .models import Category, Region, TrainingProgram


class ProgramListView(ListView):
    model = TrainingProgram
    template_name = "training/program_list.html"
    context_object_name = "programs"
    paginate_by = 10

    def get_queryset(self):
        queryset = TrainingProgram.get_active_programs()
        region_id = self.request.GET.get("region")
        category_id = self.request.GET.get("category")
        if region_id:
            queryset = queryset.filter(region_id=region_id)

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        search = self.request.GET.get("q")
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["regions"] = Region.with_program_counts()
        context["categories"] = Category.with_program_counts()
        context["selected_region"] = self.request.GET.get("region", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class ProgramDetailView(DetailView):
    model = TrainingProgram
    template_name = "training/program_detail.html"
    context_object_name = "program"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return TrainingProgram.objects.select_related("region", "category")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["program_summary"] = self.object.get_summary()
        context["is_long"] = self.object.is_long_program
        return context

class RegionListView(ListView):
    model = Region
    template_name = "training/region_list.html"
    context_object_name = "regions"

    def get_queryset(self):
        return Region.with_program_counts()

class RegionDetailView(DetailView):
    model = Region
    template_name = "training/region_detail.html"
    context_object_name = "region"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Region.objects.prefetch_related(
            Prefetch(
                "programs",
                queryset=TrainingProgram.objects
                         .filter(is_active=True)
                         .select_related("category")            # Task 1.3.2
                         .order_by("-created_at"),
            )
        )


class CategoryListView(ListView):
    model = Category
    template_name = "training/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.with_program_counts()


class CategoryDetailView(DetailView):
    model = Category
    template_name = "training/category_detail.html"
    context_object_name = "category"
    slug_field = "name"
    slug_url_kwarg = "name"

    def get_queryset(self):
        return Category.objects.prefetch_related(
            Prefetch(
                "programs",
                queryset=TrainingProgram.objects
                         .filter(is_active=True)
                         .select_related("region")              # Task 1.3.2
                         .order_by("-created_at"),
            )
        )