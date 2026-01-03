import pytest
from django.conf import settings
from django.urls import reverse


pytestmark = pytest.mark.django_db


class TestContent:
    """Тестирование содержимого страниц."""

    def test_news_count_on_home_page(
        self,
        multiple_news,
        anonymous_client
    ):
        """Количество новостей на главной странице — не более 10."""
        url = reverse('news:home')
        response = anonymous_client.get(url)
        object_list = response.context['object_list']
        # Проверяем, что количество новостей не превышает настройку
        assert len(object_list) <= settings.NEWS_COUNT_ON_HOME_PAGE
        # Конкретно проверяем, что не более 10
        assert len(object_list) <= 10

    def test_news_sorted_by_date(
        self,
        multiple_news,
        anonymous_client
    ):
        """Новости отсортированы от самой свежей к самой старой."""
        url = reverse('news:home')
        response = anonymous_client.get(url)
        object_list = response.context['object_list']

        # Проверяем, что есть новости
        assert len(object_list) > 0

        # Проверяем сортировку по убыванию даты
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates

    def test_comments_sorted_chronologically(
        self, news_with_comments, anonymous_client
    ):
        """Комментарии отсортированы в хронологическом порядке."""
        url = reverse('news:detail', args=[news_with_comments.pk])
        response = anonymous_client.get(url)

        # Получаем комментарии из контекста новости
        news_obj = response.context['object']
        # Используем related_name или дефолтный comment_set
        comments = list(news_obj.comment_set.all())

        # Проверяем, что есть комментарии
        assert len(comments) > 0

        # Проверяем сортировку по возрастанию времени создания
        created_times = [comment.created for comment in comments]
        sorted_times = sorted(created_times)
        assert created_times == sorted_times

    def test_anonymous_user_no_comment_form(
        self,
        news,
        anonymous_client
    ):
        """
        Анонимному пользователю 
        недоступна форма для отправки комментария.
        """
        url = reverse('news:detail', args=[news.pk])
        response = anonymous_client.get(url)
        # Проверяем, что формы нет в контексте
        assert 'form' not in response.context

    def test_authenticated_user_has_comment_form(
        self,
        news,
        author_client
    ):
        """
        Авторизованному пользователю 
        доступна форма для отправки комментария.
        """
        url = reverse('news:detail', args=[news.pk])
        response = author_client.get(url)
        # Проверяем, что форма есть в контексте
        assert 'form' in response.context

        # Проверяем, что это правильная форма
        from news.forms import CommentForm
        form = response.context['form']
        assert isinstance(form, CommentForm)

    @pytest.mark.parametrize(
        'parametrized_client, has_form',
        (
            (pytest.lazy_fixture('anonymous_client'), False),
            (pytest.lazy_fixture('author_client'), True),
        )
    )
    def test_comment_form_availability(
        self,
        news,
        parametrized_client,
        has_form
    ):
        """Форма комментариев доступна только авторизованным пользователям."""
        url = reverse('news:detail', args=[news.pk])
        response = parametrized_client.get(url)

        if has_form:
            assert 'form' in response.context
            from news.forms import CommentForm
            assert isinstance(response.context['form'], CommentForm)
        else:
            assert 'form' not in response.context
