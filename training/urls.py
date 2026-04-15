from django.urls import path

from . import views

app_name = "training"

urlpatterns = [
    path("", views.ProgramListView.as_view(), name="program_list"),
    path("<int:pk>/", views.ProgramDetailView.as_view(), name="program_detail"),
    path("regions/", views.RegionListView.as_view(), name="region_list"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
]
