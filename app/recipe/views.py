"""Views for the recipe APIs."""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer

from core.models import Recipe, Tag
from recipe import serializers


# ModelViewSet specialy to work with models
# GET /api/recipe/recipes/ – List all recipes (list action)
# POST /api/recipe/recipes/ – Create a new recipe (create action)
# GET /api/recipe/recipes/{id}/ – Retrieve a specific recipe by its ID (retrieve action)
# PUT /api/recipe/recipes/{id}/ – Update a recipe by its ID (update action)
# PATCH /api/recipe/recipes/{id}/ – Partially update a recipe by its ID (partial_update action)
# DELETE /api/recipe/recipes/{id}/ – Delete a recipe by its ID (destroy action)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    # objects avaliable for this view set
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class or serializers.RecipeDetailSerializer

    # Validated serializer, values should be correct
    def perform_create(self, serializer:BaseSerializer):
        """Create a new recipe."""
        # Save authenticated user into serializer
        serializer.save(user=self.request.user)


# ListModelMixin - Listing functionality
# GenericViewSet - Can throw in mixin for custom viewset
class TagViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tags for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
