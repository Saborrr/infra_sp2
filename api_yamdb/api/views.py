from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import (CharFilter, DjangoFilterBackend,
                                           FilterSet)
from http import HTTPStatus
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from .mixins import CustomViewSet
from .permissions import (AdminModeratorAuthorPermission, AdminOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          CreateUserSerializer, GenreSerializer,
                          GetTokenSerializer, ReviewSerializer,
                          TitleGetSerializer, TitlePostSerializer,
                          UserSerializer)


User = get_user_model()


class CategoryViewSet(CustomViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class GenreViewSet(CustomViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class TitleFilter(FilterSet):
    category = CharFilter(field_name='category__slug',)
    genre = CharFilter(field_name='genre__slug',)
    name = CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.annotate(rating=Avg('reviews_title__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleGetSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Просмотр, создание, редактирование и удаление отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews_title.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Просмотр, создание, редактирование и удаление комментариев отзывов."""

    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_review(self):
        return get_object_or_404(Review,
                                 pk=self.kwargs.get('review_id'),
                                 title__pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_review().comments_review.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=(permissions.IsAuthenticated,),
        url_name='me',
        url_path='me'
    )
    def me(self, request, *args, **kwargs):
        intanse = self.request.user
        serializer = self.get_serializer(intanse)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                intanse, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=self.request.user.role, partial=True)
        return Response(serializer.data)


class APIGetToken(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = request.data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'username': 'Такого пользователя не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'token': str(RefreshToken.for_user(user).access_token)},
            status=status.HTTP_201_CREATED
        )


@api_view(['POST'])
def user_create_view(request):
    email = request.data.get('email')
    username = request.data.get('username')
    if User.objects.filter(username=username, email=email).exists():
        send_confirmation_code(username, email)
        return Response(request.data, status=status.HTTP_200_OK)
    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    send_confirmation_code(username, email)
    return Response(serializer.data, status=HTTPStatus.OK)


def send_confirmation_code(username, email):
    user = get_object_or_404(User, email=email, username=username)
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    MESSAGE = (
        f'Добрый день {username}! Код - {user.confirmation_code}'
    )
    send_mail(
        message=MESSAGE,
        subject='Код подтверждения',
        recipient_list=[user.email],
        from_email=settings.FROM_EMAIL
    )
    user.save()
