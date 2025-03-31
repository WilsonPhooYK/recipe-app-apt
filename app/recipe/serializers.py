"""
Serializers for recipe APIs
"""
from typing import Any, cast
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""
    class Meta: # type:ignore
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta: # type:ignore
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes. (By default readonly)"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta: # type:ignore
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags: Any, recipe: Recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        recipe_tags = cast(Any, recipe.tags) # type: ignore
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe_tags.add(tag_obj) # type: ignore

    def _get_or_create_ingredients(self, ingredients: Any, recipe: Recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        recipe_ingredients = cast(Any, recipe.ingredients) # type: ignore
        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipe_ingredients.add(ingredient_obj)


    def create(self, validated_data: Any):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance: Recipe, validated_data: Any):
        """Update a recipe"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear() # type: ignore
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        # Assign everything else to instance except for tags
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# Extension of RecipeSerializer
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {
            'image': {
                'required': 'True'
            }
        }
