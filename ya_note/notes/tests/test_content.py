from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):
    """Тестирование содержимого страниц."""

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

        # Создаем заметки для автора
        cls.note1 = Note.objects.create(
            title='Заметка 1 автора',
            text='Текст заметки 1',
            slug='note-1',
            author=cls.author
        )
        cls.note2 = Note.objects.create(
            title='Заметка 2 автора',
            text='Текст заметки 2',
            slug='note-2',
            author=cls.author
        )

        # Создаем заметку для другого пользователя
        cls.other_note = Note.objects.create(
            title='Заметка читателя',
            text='Текст чужой заметки',
            slug='other-note',
            author=cls.reader
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_note_in_list_context(self):
        """Отдельная заметка передается в object_list контекста."""
        response = self.author_client.get(reverse('notes:list'))
        object_list = response.context['object_list']

        # Проверяем, что заметки автора есть в списке
        self.assertIn(self.note1, object_list)
        self.assertIn(self.note2, object_list)

        # Проверяем, что у каждой заметки есть все необходимые поля
        for note in object_list:
            self.assertIsInstance(note, Note)
            self.assertTrue(hasattr(note, 'title'))
            self.assertTrue(hasattr(note, 'text'))
            self.assertTrue(hasattr(note, 'slug'))
            self.assertTrue(hasattr(note, 'author'))

    def test_one_user_notes_not_in_another_user_list(self):
        """Заметки одного пользователя не попадают в список другого."""
        # Получаем список заметок автора
        response = self.author_client.get(reverse('notes:list'))
        author_notes = response.context['object_list']

        # Проверяем, что в списке автора нет чужих заметок
        self.assertNotIn(self.other_note, author_notes)

        # Проверяем, что в списке автора только его заметки
        for note in author_notes:
            self.assertEqual(note.author, self.author)

    def test_forms_in_create_and_edit_pages(self):
        """На страницы создания и редактирования передаются формы."""
        # Страница создания
        response = self.author_client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        # Страница редактирования
        response = self.author_client.get(
            reverse('notes:edit', args=[self.note1.slug])
        )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        # Проверяем, что форма редактирования содержит данные заметки
        form = response.context['form']
        self.assertEqual(form.instance, self.note1)
