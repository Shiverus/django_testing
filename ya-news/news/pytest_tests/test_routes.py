import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


class TestRoutes:
    """Тестирование маршрутов приложения news."""

    def test_home_page_available_to_anonymous(
        self,
        anonymous_client
    ):
        """Главная страница доступна анонимному пользователю."""
        url = reverse('news:home')
        response = anonymous_client.get(url)
        assert response.status_code == 200

    def test_news_detail_available_to_anonymous(
        self,
        anonymous_client,
        news
    ):
        """Страница отдельной новости доступна анонимному пользователю."""
        url = reverse('news:detail', args=[news.pk])
        response = anonymous_client.get(url)
        assert response.status_code == 200

    def test_comment_edit_available_to_author(
        self,
        author_client,
        comment
    ):
        """Страница редактирования комментария доступна автору."""
        url = reverse('news:edit', args=[comment.pk])
        response = author_client.get(url)
        assert response.status_code == 200

    def test_comment_delete_available_to_author(
        self,
        author_client,
        comment
    ):
        """Страница удаления комментария доступна автору."""
        url = reverse('news:delete', args=[comment.pk])
        response = author_client.get(url)
        assert response.status_code == 200

    def test_anonymous_redirected_on_comment_edit(
        self,
        anonymous_client, comment
    ):
        """Анонимный пользователь перенаправляется на авторизацию."""
        url = reverse('news:edit', args=[comment.pk])
        response = anonymous_client.get(url)
        # Проверяем редирект (код 302)
        assert response.status_code == 302
        # Проверяем, что URL содержит 'login'
        assert 'login' in response.url

    def test_anonymous_redirected_on_comment_delete(
        self,
        anonymous_client, comment
    ):
        """Пользователь перенаправляется на авторизацию."""
        url = reverse('news:delete', args=[comment.pk])
        response = anonymous_client.get(url)
        # Проверяем редирект (код 302)
        assert response.status_code == 302
        # Проверяем, что URL содержит 'login'
        assert 'login' in response.url

    def test_reader_cannot_edit_others_comment(
        self,
        reader_client, comment
    ):
        """Пользователь не может редактировать чужие комментарии."""
        url = reverse('news:edit', args=[comment.pk])
        response = reader_client.get(url)
        assert response.status_code == 404

    def test_reader_cannot_delete_others_comment(
        self,
        reader_client,
        comment
    ):
        """Авторизованный пользователь не может удалять чужие комментарии."""
        url = reverse('news:delete', args=[comment.pk])
        response = reader_client.get(url)
        assert response.status_code == 404

    # Простая версия без параметризации
    def test_comment_pages_availability_to_author(
        self,
        author_client, comment
    ):
        """Страницы комментариев доступны автору."""
        urls = (
            ('news:edit', (comment.pk,)),
            ('news:delete', (comment.pk,)),
        )

        for name, args in urls:
            url = reverse(name, args=args)
            response = author_client.get(url)
            assert response.status_code == 200

    def test_comment_pages_not_available_to_reader(
        self,
        reader_client, comment
    ):
        """Страницы комментариев не доступны другому пользователю."""
        urls = (
            ('news:edit', (comment.pk,)),
            ('news:delete', (comment.pk,)),
        )

        for name, args in urls:
            url = reverse(name, args=args)
            response = reader_client.get(url)
            assert response.status_code == 404

    @pytest.mark.parametrize(
        'url_name',
        [
            'login',
            'logout',
        ]
    )
