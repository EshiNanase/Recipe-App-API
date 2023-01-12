"""
Serializers for Recipe model
"""
from rest_framework.serializers import ModelSerializer
from core.models import Recipe, Tag


class TagSerializer(ModelSerializer):
    """Serializer: Tags-list"""
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(ModelSerializer):
    """Serializer: Recipes-list"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'tags', 'price', 'link')
        read_only_fields = ('id',)

    def create(self, validated_data):
        """Create a recipe"""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_object, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_object)
        return recipe


class RecipeDetailSerializer(ModelSerializer):
    """Serializer: Recipe-detail"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description', 'price')
