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
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter'
            )
        ]
    )
)
class RecipeViewSet(ModelViewSet):
    """View: Managing recipe APIs"""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Converting strings to ints"""
        return [int(i) for i in qs.split(',')]

    def get_queryset(self):
        """Returning queryset sorted from latest created to newest"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)
        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes'
            ),
        ]
    )
)
class AbsoluteViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """View: Non duplicating the code below in viewsets"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returning Tags for a particular user"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-id').distinct()


class TagViewSet(AbsoluteViewSet):
    """View: Managing tag APIs"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(AbsoluteViewSet):
    """View: Managing ingredient APIs"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
