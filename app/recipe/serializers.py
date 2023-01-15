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
        fields = ('id', 'name', 'tags', 'time_minutes', 'link')
        read_only_fields = ('id',)

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a recipe"""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        
        return recipe

    def update(self, instance, validated_data):
        """Update recipe"""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
    
        return instance


class RecipeDetailSerializer(ModelSerializer):
    """Serializer: Recipe-detail"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description', 'price')
