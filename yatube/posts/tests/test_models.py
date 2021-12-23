from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post, Comment, Follow
from django.utils import timezone

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='I think all people like holidays',
        )

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post

        field_object_name = {
            post: self.post.text,
        }
        for value, expected in field_object_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    str(post), expected[:15]
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group

        field_object_name = {
            group: self.group.title,
        }
        for value, expected in field_object_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    str(group), expected
                )

class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.pub_date = timezone.now()
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text',
        )
        cls.comment = Comment.objects.create(
            post_id=cls.post.id,
            author=cls.author,
            text='test_comment',
            created=cls.pub_date,
        )
        
    def test_comment_model_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = CommentModelTest.comment

        field_object_name = {
            comment: self.comment.text,
        }
        for value, expected in field_object_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    str(comment), expected
                )    