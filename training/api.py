from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import TrainingProgram, Region, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'slug']


class TrainingProgramSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    category_name = serializers.CharField(source='category.get_name_display', read_only=True)
    duration_display = serializers.CharField(read_only=True)

    class Meta:
        model = TrainingProgram
        fields = [
            'id', 'title', 'slug', 'description', 'duration_weeks',
            'duration_display', 'eligibility', 'is_active',
            'region_name', 'category_name',
        ]


class TrainingProgramListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TrainingProgramSerializer
    queryset = TrainingProgram.get_active_programs() 