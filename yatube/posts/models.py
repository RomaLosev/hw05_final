from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Группа, к которой относится пост'
    )
    slug = models.SlugField(
        unique=True, max_length=100,
        default='title',
        verbose_name='URL адресс группы',
        help_text='URL адресс группы'
    )
    description = models.TextField(
        help_text='О чём эта группа',
        verbose_name='Описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        help_text='Писать тут',
        verbose_name='Текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Дата публикации',
        verbose_name='Дата',
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text='Автор поста',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Группа к которой относится пост',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Cтатья с комментариями',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Напишите комменатрий',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Отслеживается',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique subs'),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        def __str__(self):
            return f'{self.user} подписан на {self.author}'
