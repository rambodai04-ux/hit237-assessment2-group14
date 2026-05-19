from django.urls import path

from . import views

app_name = "training"

urlpatterns = [
    path("", views.ProgramListView.as_view(), name="program_list"),
    path("programs/<slug:slug>/", views.ProgramDetailView.as_view(), name="program_detail"),

    path("regions/", views.RegionListView.as_view(), name="region_list"),
    path("regions/<slug:slug>/", views.RegionDetailView.as_view(), name="region_detail"),

    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/<str:name>/", views.CategoryDetailView.as_view(), name="category_detail"),

]
