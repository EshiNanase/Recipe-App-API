from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer, IngredientSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient


class RecipeViewSet(ModelViewSet):
    """View: Managing recipe APIs"""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returning queryset sorted from latest created to newest"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Specifying serializer for action"""
        if self.action == 'retrieve' or self.action == 'update':
            return RecipeDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Serializer saving to db"""
        serializer.save(user=self.request.user)


class TagViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """View: Managing tag APIs"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returning Tags for a particular user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')


class IngredientViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """View: Managing ingredient APIs"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')
