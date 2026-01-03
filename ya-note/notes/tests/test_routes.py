from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование маршрутов приложения notes."""

    @classmethod
    def setUpTestData(cls):
        """Создаем тестовые данные."""
        cls.author = User.objects.create_user(
            username='author',
            password='password123'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='password123'
        )
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст тестовой заметки',
            slug='test-note',
            author=cls.author
        )
        cls.client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_home_page_available_to_anonymous(self):
        """Главная страница доступна анонимному пользователю."""
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_access(self):
        """Аутентифицированному пользователю доступны страницы."""
        urls = [
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        ]

        for url_name, args in urls:
            with self.subTest(url_name=url_name):
                response = self.author_client.get(
                    reverse(url_name, args=args)
                )
                self.assertEqual(response.status_code, 200)

    def test_note_pages_available_only_to_author(self):
        """Страницы заметки доступны только автору."""
        note_pages = [
            ('notes:detail', [self.note.slug]),
            ('notes:edit', [self.note.slug]),
            ('notes:delete', [self.note.slug]),
        ]

        # Проверяем доступ автора
        for url_name, args in note_pages:
            with self.subTest(url_name=url_name, user='author'):
                response = self.author_client.get(
                    reverse(url_name, args=args)
                )
                self.assertEqual(response.status_code, 200)

        # Проверяем, что другой пользователь получает 404
        for url_name, args in note_pages:
            with self.subTest(url_name=url_name, user='reader'):
                response = self.reader_client.get(
                    reverse(url_name, args=args)
                )
                self.assertEqual(response.status_code, 404)

    def test_anonymous_user_redirected_to_login(self):
        """Анонимный пользователь перенаправляется на страницу логина."""
        urls = [
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', [self.note.slug]),
            ('notes:edit', [self.note.slug]),
            ('notes:delete', [self.note.slug]),
        ]

        for url_name, args in urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(
                    reverse(url_name, args=args),
                    follow=False
                )
                # Проверяем редирект (код 302)
                self.assertEqual(response.status_code, 302)
                # Проверяем, что URL содержит 'login'
                self.assertIn('login', response.url)
