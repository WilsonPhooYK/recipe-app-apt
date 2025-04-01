"""Views for the recipe APIs."""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.response import Response

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


# ModelViewSet specialy to work with models
# GET /api/recipe/recipes/ – List all recipes (list action)
# POST /api/recipe/recipes/ – Create a new recipe (create action)
# GET /api/recipe/recipes/{id}/ – Retrieve a specific recipe by its ID (retrieve action)
# PUT /api/recipe/recipes/{id}/ – Update a recipe by its ID (update action)
# PATCH /api/recipe/recipes/{id}/ – Partially update a recipe by its ID (partial_update action)
# DELETE /api/recipe/recipes/{id}/ – Delete a recipe by its ID (destroy action)
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ],
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    # objects avaliable for this view set
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        # 1,2,3
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        tags = self.request.query_params.get('tags') # type:ignore
        ingredients = self.request.query_params.get('ingredients') # type:ignore
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user
        ).distinct().order_by('-id') # type:ignore

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class or serializers.RecipeDetailSerializer

    # Validated serializer, values should be correct
    def perform_create(self, serializer:BaseSerializer):
        """Create a new recipe."""
        # Save authenticated user into serializer
        serializer.save(user=self.request.user)

    # A specific receipe must be specified
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                # 0 - False, 1 - True
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes',
            ),
        ],
    )
)
class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tags for authenticated user."""
        assigned_only = bool(
            # assigned_only = 0, by default
            int(self.request.query_params.get('assigned_only', 0)) # type:ignore
        )
        queryset = self.queryset
        if assigned_only:
            # Need to have recipe
            queryset = queryset.filter(recipe__isnull=False) # type:ignore

        return queryset.filter( # type:ignore
            user=self.request.user
        ).distinct().order_by('-name')


# ListModelMixin - Listing functionality
# GenericViewSet - Can throw in mixin for custom viewset
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
 

class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
