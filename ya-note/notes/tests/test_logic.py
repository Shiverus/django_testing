from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    """Тестирование бизнес-логики приложения."""

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

        cls.client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_authenticated_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        notes_count_before = Note.objects.count()

        response = self.author_client.post(
            reverse('notes:add'),
            {
                'title': 'Новая заметка',
                'text': 'Текст новой заметки',
                'slug': 'new-note'
            },
            follow=True
        )

        notes_count_after = Note.objects.count()

        # Проверяем, что заметка создана
        self.assertEqual(notes_count_after, notes_count_before + 1)

        # Проверяем редирект на страницу успеха
        self.assertRedirects(response, reverse('notes:success'))

        # Проверяем, что заметка сохранена с правильными данными
        new_note = Note.objects.get(slug='new-note')
        self.assertEqual(new_note.title, 'Новая заметка')
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()

        response = self.client.post(
            reverse('notes:add'),
            {
                'title': 'Анонимная заметка',
                'text': 'Текст анонимной заметки',
                'slug': 'anonymous-note'
            },
            follow=False  # Не следуем за редиректом
        )

        notes_count_after = Note.objects.count()

        # Проверяем, что заметка не создана
        self.assertEqual(notes_count_after, notes_count_before)

        # Проверяем, что получен редирект на логин (код 302)
        self.assertEqual(response.status_code, 302)

        # Проверяем, что URL редиректа содержит логин
        self.assertIn('login', response.url)

    def test_cannot_create_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        # Создаем первую заметку
        Note.objects.create(
            title='Первая заметка',
            text='Текст первой заметки',
            slug='duplicate-slug',
            author=self.author
        )

        notes_count_before = Note.objects.count()

        # Пытаемся создать вторую заметку с тем же slug
        response = self.author_client.post(
            reverse('notes:add'),
            {
                'title': 'Вторая заметка',
                'text': 'Текст второй заметки',
                'slug': 'duplicate-slug'
            }
        )

        notes_count_after = Note.objects.count()

        # Проверяем, что вторая заметка не создана
        self.assertEqual(notes_count_after, notes_count_before)

        # Проверяем, что остались на странице формы (статус 200)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что форма содержит ошибку
        form = response.context.get('form')
        if form:
            self.assertTrue(form.errors)
            self.assertIn('slug', form.errors)

    def test_auto_slug_generation(self):
        """Если slug не заполнен, он формируется автоматически."""
        notes_count_before = Note.objects.count()

        response = self.author_client.post(
            reverse('notes:add'),
            {
                'title': 'Заметка с автоматическим slug',
                'text': 'Текст заметки',
                'slug': ''  # Пустой slug
            },
            follow=True
        )

        notes_count_after = Note.objects.count()

        # Проверяем, что заметка создана
        self.assertEqual(notes_count_after, notes_count_before + 1)

        # Ищем созданную заметку
        note = Note.objects.get(title='Заметка с автоматическим slug')

        # Проверяем, что slug сгенерирован и не пустой
        self.assertTrue(note.slug)
        self.assertNotEqual(note.slug, '')

        # Проверяем, что slug содержит только разрешенные символы
        import re
        pattern = r'^[a-zA-Z0-9_-]+$'
        self.assertTrue(re.match(pattern, note.slug) is not None)

        # Проверяем редирект на страницу успеха
        self.assertRedirects(response, reverse('notes:success'))

    def test_user_can_edit_own_note(self):
        """Пользователь может редактировать свои заметки."""
        note = Note.objects.create(
            title='Старая заметка',
            text='Старый текст',
            slug='old-note',
            author=self.author
        )

        response = self.author_client.post(
            reverse('notes:edit', args=[note.slug]),
            {
                'title': 'Обновленная заметка',
                'text': 'Новый текст',
                'slug': 'updated-note'
            },
            follow=True
        )

        # Обновляем объект из БД
        note.refresh_from_db()

        # Проверяем обновление
        self.assertEqual(note.title, 'Обновленная заметка')
        self.assertEqual(note.text, 'Новый текст')
        self.assertEqual(note.slug, 'updated-note')

        # Проверяем редирект на страницу успеха
        self.assertRedirects(response, reverse('notes:success'))

    def test_user_cannot_edit_others_note(self):
        """Пользователь не может редактировать чужие заметки."""
        # Создаем заметку автора
        note = Note.objects.create(
            title='Заметка автора',
            text='Текст',
            slug='author-note',
            author=self.author
        )

        # Пытаемся отредактировать от имени другого пользователя
        response = self.reader_client.post(
            reverse('notes:edit', args=[note.slug]),
            {
                'title': 'Взломанная заметка',
                'text': 'Новый текст',
                'slug': 'hacked-note'
            }
        )

        # Проверяем, что получили 404
        self.assertEqual(response.status_code, 404)

        # Проверяем, что заметка не изменилась
        note.refresh_from_db()
        self.assertEqual(note.title, 'Заметка автора')
        self.assertEqual(note.slug, 'author-note')

    def test_user_can_delete_own_note(self):
        """Пользователь может удалять свои заметки."""
        note = Note.objects.create(
            title='Заметка для удаления',
            text='Текст',
            slug='to-delete',
            author=self.author
        )

        notes_count_before = Note.objects.count()

        response = self.author_client.post(
            reverse('notes:delete', args=[note.slug]),
            follow=True
        )

        notes_count_after = Note.objects.count()

        # Проверяем удаление
        self.assertEqual(notes_count_after, notes_count_before - 1)
        self.assertFalse(Note.objects.filter(slug='to-delete').exists())

        # Проверяем редирект на страницу успеха
        self.assertRedirects(response, reverse('notes:success'))

    def test_user_cannot_delete_others_note(self):
        """Пользователь не может удалять чужие заметки."""
        note = Note.objects.create(
            title='Чужая заметка',
            text='Текст',
            slug='others-note',
            author=self.author
        )

        notes_count_before = Note.objects.count()

        # Пытаемся удалить от имени другого пользователя
        response = self.reader_client.post(
            reverse('notes:delete', args=[note.slug])
        )

        notes_count_after = Note.objects.count()

        # Проверяем, что получили 404 и заметка не удалена
        self.assertEqual(response.status_code, 404)
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertTrue(Note.objects.filter(slug='others-note').exists())
