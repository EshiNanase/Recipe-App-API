from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer, IngredientSerializer, \
    ImageSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient
from http import HTTPStatus
from rest_framework.decorators import action
from rest_framework.response import Response


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
        elif self.action == 'upload_image':
            return ImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Serializer saving to db"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Uploads an image"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, HTTPStatus.OK)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


class AbsoluteViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """View: Non duplicating the code below in viewsets"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returning Tags for a particular user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')


class TagViewSet(AbsoluteViewSet):
    """View: Managing tag APIs"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(AbsoluteViewSet):
    """View: Managing ingredient APIs"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
