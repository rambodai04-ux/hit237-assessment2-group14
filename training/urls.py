from django.urls import path

from . import views
from .api import TrainingProgramListAPIView

app_name = "training"

urlpatterns = [
    path("", views.ProgramListView.as_view(), name="program_list"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("programs/<slug:slug>/", views.ProgramDetailView.as_view(), name="program_detail"),
    path("programs/<slug:slug>/save/", views.SaveProgramView.as_view(), name="save_program"),
    path("programs/<slug:slug>/unsave/", views.UnsaveProgramView.as_view(), name="unsave_program"),


    path("regions/", views.RegionListView.as_view(), name="region_list"),
    path("regions/<slug:slug>/", views.RegionDetailView.as_view(), name="region_detail"),

    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/<str:name>/", views.CategoryDetailView.as_view(), name="category_detail"),

    path("api/programs/", TrainingProgramListAPIView.as_view(), name="api_program_list"),

]
