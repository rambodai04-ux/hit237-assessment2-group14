from django.views.generic import DetailView, ListView

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
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["regions"] = Region.objects.all()
        context["categories"] = Category.objects.all()
        context["selected_region"] = self.request.GET.get("region", "")
        context["selected_category"] = self.request.GET.get("category", "")
        return context


class ProgramDetailView(DetailView):
    model = TrainingProgram
    template_name = "training/program_detail.html"
    context_object_name = "program"


class RegionListView(ListView):
    model = Region
    template_name = "training/region_list.html"
    context_object_name = "regions"

    def get_queryset(self):
        return Region.objects.prefetch_related("programs")


class CategoryListView(ListView):
    model = Category
    template_name = "training/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.prefetch_related("programs")
