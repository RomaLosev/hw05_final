import shutil
import tempfile
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post, Group
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.author = User.objects.create_user(username='test_author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_description'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.author,
            image=cls.image
        )

        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test_group_slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'test_author'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': '1'}
            ): 'posts/create_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
    shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL адресс использует соответствующий шаблон"""
        for reverse_name, template in (
            PostViewsTests.templates_pages_names.items()
        ):
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTests.authorized_author.get(
                    reverse_name, follow=True
                )
                self.assertTemplateUsed(response, template)

    def check_post(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.image, self.post.image)

    def test_index_show_correct_context(self):
        """Главная страница сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_client.get(
            reverse('posts:index')
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_group_list_show_correct_context(self):
        """Cтраница группы сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_post_profile_show_correct_context(self):
        """Страница профиля сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(
            reverse('posts:profile', args=['test_author'])
        )
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_post_detail_show_correct_context(self):
        """Страница поста сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(
            reverse('posts:post_detail', args=[1])
        )
        post = response.context['post']
        self.check_post(post)

    def test_post_create_show_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Страница редактирования сформирована с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(
            reverse('posts:post_edit', args=[1])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_shows_on_pages(self):
        """Проверяем, что новый пост показывается на нужных страницах"""

        self.new_group = Group.objects.create(
            title='new_group',
            slug='new_slug',
            description='something',
        )

        self.new_post = Post.objects.create(
            text='Новый текст',
            group=self.new_group,
            author=self.author,
        )

        form_data = {
            'text': 'Новый текст',
            'group': 'new_group',
        }
        response = self.authorized_author.post(
            reverse('posts:index'),
            data=form_data,
        )
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, 'Новый текст')

        response = self.authorized_author.post(
            reverse('posts:group_list', args=['new_group']),
            data=form_data,
        )
        self.assertEqual(first_post.text, 'Новый текст')

        response = self.authorized_author.post(
            reverse('posts:profile', args=[self.author]),
            data=form_data,
        )
        self.assertEqual(first_post.text, 'Новый текст')

        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='posts_author',
        )
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='Тестовое описание группы',
        )
        cls.post = [
            Post.objects.create(
                text='Пост №' + str(i),
                author=PaginatorViewsTest.user,
                group=PaginatorViewsTest.group
            )
            for i in range(13)]

    def test_index_page_contains_ten_records(self):

        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class CacheIndexPageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='posts_author',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        content = self.authorized_client.get(reverse('posts:index')).content
        Post.objects.create(
            text='Пост №1',
            author=self.user,
        )
        content_1 = self.authorized_client.get(reverse('posts:index')).content
        self.assertEqual(content, content_1)
        cache.clear()
        content_2 = self.authorized_client.get(reverse('posts:index')).content
        self.assertNotEqual(content_1, content_2)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='posts_author',
        )
        cls.follower = User.objects.create(
            username='follower',
        )
        cls.unfollower = User.objects.create(
            username='unfollower',
        )
        cls.post = Post.objects.create(
            author=FollowViewsTest.author,
            text='Рандомный текст статьи',
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.unfollower)

        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_can_follow(self):
        """Авторизованный пользователь может подписываться и отписываться"""

        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        page_object = response.context['page_obj']
        self.assertEqual((len(page_object)), 0)

        self.follower_client.get(
            reverse('posts:profile_follow', args=[self.author])
        )

        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        page_object = response.context['page_obj']
        self.assertEqual((len(page_object)), 1)
    
    def test_can_unfollow(self):
        self.follower_client.get(
            reverse('posts:profile_follow', args=[self.author])
        )
        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        page_object = response.context['page_obj']
        self.assertEqual((len(page_object)), 1)

        self.follower_client.get(
            reverse('posts:profile_unfollow', args=[self.author])
        )

        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        page_object = response.context['page_obj']
        self.assertEqual((len(page_object)), 0)

    def test_follow_post(self):
        """Проверяем что пост не появляется у того, кто не подписан"""

        self.follower_client.get(
            reverse('posts:profile_follow', args=[self.author])
        )
        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        post_object = response.context['page_obj']

        self.assertEqual((len(post_object)), 1)

        response = self.unfollower_client.get(
            reverse('posts:follow_index')
        )
        post_object = response.context['page_obj']
        self.assertEqual((len(post_object)), 0)
