from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from reviews.constants import MAX_SCORE, MIN_SCORE
from reviews.validators import validate_year
from users.models import User


class Category(models.Model):
    """Тут описана модель 'Категория'."""

    name = models.CharField(max_length=256,
                            verbose_name='Категория',
                            help_text='Напишите здесь категорию',
                            unique=True)
    slug = models.SlugField(
        max_length=50,
        verbose_name='slug',
        unique=True,
        validators=[RegexValidator(
                    regex=r'^[-a-zA-Z0-9_]+$',
                    message='Слаг категории содержит недопустимый символ')])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Тут описана модель 'Жанр'."""

    name = models.CharField(max_length=256,
                            verbose_name='Жанр',
                            help_text='Напишите здесь жанр',
                            unique=True)
    slug = models.SlugField(
        max_length=50,
        verbose_name='slug',
        unique=True,
        validators=[RegexValidator(
                    regex=r'^[-a-zA-Z0-9_]+$',
                    message='Слаг категории содержит недопустимый символ')])

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Тут описана модель 'Произведения'."""

    name = models.CharField(max_length=256,
                            verbose_name='Название',
                            help_text='Название произведения')
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        help_text='Год выпуска произведения',
        null=True,
        db_index=True,
        validators=(validate_year,))
    description = models.CharField(verbose_name='Описание',
                                   help_text='Описание произведения',
                                   max_length=2000,
                                   blank=True)
    genre = models.ManyToManyField(Genre,
                                   verbose_name='Жанр',
                                   help_text='Жанр произведения',
                                   related_name='titles')
    category = models.ForeignKey(Category,
                                 verbose_name='Категория',
                                 help_text='Категория выбранного произведения',
                                 on_delete=models.SET_NULL,
                                 related_name='titles',
                                 null=True)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Вспомогательный класс, связывающий жанры и произведения."""

    genre = models.ForeignKey(Genre,
                              on_delete=models.CASCADE,
                              verbose_name='Жанр')
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              verbose_name='Произведение')

    class Meta:
        verbose_name = 'Соответствие жанра и произведения'
        verbose_name_plural = 'Таблица соответствия жанров и произведений'
        ordering = ('id',)

    def __str__(self):
        return f'{self.title} принадлежит жанру(ам) {self.genre}'


class Review(models.Model):
    """Модель Review (Отзывы)."""

    text = models.TextField(verbose_name='Текст отзыва',
                            help_text='Оставьте отзыв на произведение')
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              verbose_name=(
                                  'Произведение, к которому относится отзыв'),
                              related_name='reviews_title')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор отзыва',
                               related_name='reviews_author')
    score = models.PositiveSmallIntegerField(
        verbose_name=f'Оценка от {MIN_SCORE} до {MAX_SCORE}',
        help_text=f'Оцените произведение от {MIN_SCORE} до {MAX_SCORE}',
        validators=(
            MinValueValidator(
                MIN_SCORE, (f'Оценка может быть не менее {MIN_SCORE}')),
            MaxValueValidator(
                MAX_SCORE, (f'Оценка может быть не более {MAX_SCORE}')),),
        default=MIN_SCORE)
    pub_date = models.DateTimeField(verbose_name='Дата публикации отзыва',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [models.UniqueConstraint(fields=['title', 'author'],
                                               name='unique_title_author')]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель Comment (Комментарии)."""

    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Прокомментируйте отзыв на произведение')
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               verbose_name=(
                                   'Комментируемый отзыв'),
                               related_name='comments_review')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор комментария',
                               related_name='comments_author')
    pub_date = models.DateTimeField(verbose_name='Дата публикации комментария',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
