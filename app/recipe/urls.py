"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
# Creates recipe/recipes and then recipe/recipes:get recipe/recipes:post, etc form the viewset
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)

# For reverse urls
app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]