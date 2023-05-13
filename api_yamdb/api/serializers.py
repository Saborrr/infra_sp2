from django.conf import settings

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from users.validators import username_validation


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'rating',
                  'description',
                  'genre',
                  'category',)


class TitlePostSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(queryset=Category.objects.all(),
                                slug_field='slug')
    genre = SlugRelatedField(queryset=Genre.objects.all(),
                             slug_field='slug',
                             many=True)

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('title', )

    def validate(self, data):
        if self.context.get('request').method != 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs['title_id']
        if Review.objects.filter(author=author, title__id=title_id).exists():
            raise serializers.ValidationError(
                'Отзыв на данное произведение уже создан!')
        return data

    def validate_score(self, value):
        if value not in range(1, 11):
            raise serializers.ValidationError(
                'Оценка произведения должна быть от 1 до 10!')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review', )


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    """Сериализация модели User."""
    username = serializers.CharField(
        required=True,
        max_length=settings.MAX_LENGTH_USERNAME,
        validators=[
            username_validation,
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = User


class CreateUserSerializer(serializers.ModelSerializer):
    """Создание пользователя."""
    username = serializers.CharField(
        validators=(
            username_validation,
            UniqueValidator(queryset=User.objects.all(),),
        ),
        max_length=settings.MAX_LENGTH_USERNAME,
        required=True
    )
    email = serializers.EmailField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        ),
        max_length=settings.MAX_LENGTH_EMAIL,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')
