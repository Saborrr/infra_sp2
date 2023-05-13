from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (UserViewSet, APIGetToken, user_create_view,
                       CategoryViewSet, GenreViewSet, TitleViewSet,
                       ReviewViewSet, CommentViewSet)

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('categories', CategoryViewSet, basename='Category')
v1_router.register('genres', GenreViewSet, basename='Genre')
v1_router.register('titles', TitleViewSet, basename='Title')
v1_router.register('users', UserViewSet, basename='users')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')

v1_urls = [
    path('auth/signup/', user_create_view, name='signup'),
    path('auth/token/', APIGetToken.as_view(), name='get_token'),
]

urlpatterns = [
    path('', include(v1_router.urls)),
    path('v1/', include(v1_router.urls)),
    path('v1/', include(v1_urls)),
]
