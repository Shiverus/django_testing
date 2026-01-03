import pytest
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


pytestmark = pytest.mark.django_db


class TestLogic:
    """Тестирование логики приложения."""

    def test_anonymous_cannot_post_comment(
        self,
        news,
        anonymous_client
    ):
        """Анонимный пользователь не может отправить комментарий."""
        comments_before = Comment.objects.count()

        url = reverse('news:detail', args=[news.pk])
        response = anonymous_client.post(
            url,
            {'text': 'Новый комментарий'}
        )

        comments_after = Comment.objects.count()

        # Проверяем, что комментарий не создан
        assert comments_after == comments_before
        # Проверяем редирект (код 302)
        assert response.status_code == 302
        # Проверяем, что URL содержит 'login'
        assert 'login' in response.url

    def test_authenticated_can_post_comment(
        self,
        news,
        author_client
    ):
        """Авторизованный пользователь может отправить комментарий."""
        comments_before = Comment.objects.count()

        url = reverse('news:detail', args=[news.pk])
        response = author_client.post(
            url,
            {'text': 'Новый комментарий от автора'},
            follow=True
        )

        comments_after = Comment.objects.count()

        # Проверяем, что комментарий создан
        assert comments_after == comments_before + 1

        # Проверяем, что мы на странице новости (статус 200)
        assert response.status_code == 200

        # Проверяем, что комментарий сохранен с правильными данными
        new_comment = Comment.objects.last()
        assert new_comment.text == 'Новый комментарий от автора'
        assert new_comment.news == news
        assert new_comment.author.username == 'author'

    @pytest.mark.parametrize('bad_word', BAD_WORDS)
    def test_comment_with_bad_words_rejected(
        self,
        news,
        author_client,
        bad_word
    ):
        """Комментарий с запрещёнными словами не публикуется."""
        comments_before = Comment.objects.count()

        url = reverse('news:detail', args=[news.pk])
        response = author_client.post(
            url,
            {'text': f'Текст с запрещенным словом {bad_word}'}
        )

        comments_after = Comment.objects.count()

        # Проверяем, что комментарий не создан
        assert comments_after == comments_before

        # Проверяем, что остались на странице (статус 200)
        assert response.status_code == 200

        # Проверяем, что форма содержит ошибку
        form = response.context.get('form')
        assert form is not None
        assert form.errors
        assert 'text' in form.errors
        assert WARNING in str(form.errors['text'])

    def test_author_can_edit_own_comment(
        self,
        comment,
        author_client
    ):
        """Авторизованный пользователь может редактировать свои комментарии."""
        new_text = 'Обновленный текст комментария'

        url = reverse('news:edit', args=[comment.pk])
        response = author_client.post(
            url,
            {'text': new_text},
            follow=True
        )

        # Обновляем объект из БД
        comment.refresh_from_db()

        # Проверяем обновление
        assert comment.text == new_text

        # Проверяем, что мы на странице новости (статус 200)
        assert response.status_code == 200

    def test_author_can_delete_own_comment(
        self,
        comment,
        author_client
    ):
        """
        Авторизованный пользователь 
        может удалять свои комментарии.
        """
        comments_before = Comment.objects.count()
        comment_id = comment.pk

        url = reverse('news:delete', args=[comment.pk])
        response = author_client.post(url, follow=True)

        comments_after = Comment.objects.count()

        # Проверяем удаление
        assert comments_after == comments_before - 1
        assert not Comment.objects.filter(pk=comment_id).exists()

        # Проверяем, что мы на странице новости (статус 200)
        assert response.status_code == 200

    def test_reader_cannot_edit_others_comment(
        self,
        comment,
        reader_client
    ):
        """
        Авторизованный пользователь 
        не может редактировать чужие комментарии.
        """
        original_text = comment.text

        url = reverse('news:edit', args=[comment.pk])
        response = reader_client.post(
            url,
            {'text': 'Попытка редактирования'}
        )

        # Проверяем, что получили 404
        assert response.status_code == 404

        # Проверяем, что комментарий не изменился
        comment.refresh_from_db()
        assert comment.text == original_text

    def test_reader_cannot_delete_others_comment(
        self,
        comment,
        reader_client
    ):
        """
        Авторизованный пользователь 
        не может удалять чужие комментарии.
        """
        comments_before = Comment.objects.count()

        url = reverse('news:delete', args=[comment.pk])
        response = reader_client.post(url)

        comments_after = Comment.objects.count()

        # Проверяем, что получили 404
        assert response.status_code == 404

        # Проверяем, что комментарий не удален
        assert comments_after == comments_before
        assert Comment.objects.filter(pk=comment.pk).exists()

    # Простые версии без параметризации
    def test_author_can_access_comment_pages(
        self,
        author_client,
        comment
    ):
        """
        Автор может получить доступ 
        к страницам редактирования и удаления.
        """
        urls = (
            ('news:edit', (comment.pk,)),
            ('news:delete', (comment.pk,)),
        )

        for name, args in urls:
            url = reverse(name, args=args)
            response = author_client.get(url)
            assert response.status_code == 200

    def test_reader_cannot_access_others_comment_pages(
        self,
        reader_client,
        comment
    ):
        """
        Другой пользователь не может получить доступ 
        к страницам редактирования и удаления чужих комментариев.
        """
        urls = (
            ('news:edit', (comment.pk,)),
            ('news:delete', (comment.pk,)),
        )

        for name, args in urls:
            url = reverse(name, args=args)
            response = reader_client.get(url)
            assert response.status_code == 404
