"""
Serializers for Recipe model
"""
from rest_framework.serializers import ModelSerializer
from core.models import Recipe


class RecipeSerializer(ModelSerializer):
    """Serializer: Recipes-all"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'time_minutes', 'link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(ModelSerializer):
    """Serializer: Recipe-detail"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description', 'price')
