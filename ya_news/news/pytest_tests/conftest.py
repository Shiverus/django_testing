import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from datetime import datetime, timedelta

from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def author(django_user_model):
    """Фикстура для создания автора."""
    return django_user_model.objects.create_user(
        username='author',
        password='password123'
    )


@pytest.fixture
def reader(django_user_model):
    """Фикстура для создания читателя."""
    return django_user_model.objects.create_user(
        username='reader',
        password='password123'
    )


@pytest.fixture
def author_client(author):
    """Клиент автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Клиент читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def anonymous_client():
    """Анонимный клиент."""
    return Client()


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
        date=datetime.today()
    )


@pytest.fixture
def comment(author, news):
    """Фикстура для создания комментария автора."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий автора'
    )


@pytest.fixture
def other_comment(reader, news):
    """Фикстура для создания комментария другого пользователя."""
    return Comment.objects.create(
        news=news,
        author=reader,
        text='Комментарий читателя'
    )


@pytest.fixture
def multiple_news():
    """Создание нескольких новостей для тестирования."""
    news_list = []
    for i in range(15):  # Создаем 15 новостей
        news = News.objects.create(
            title=f'Новость {i}',
            text=f'Текст новости {i}',
            date=datetime.today() - timedelta(days=i)  # Разные даты
        )
        news_list.append(news)
    return news_list


@pytest.fixture
def news_with_comments(news, author):
    """Новость с несколькими комментариями."""
    # Создаем комментарии с небольшими задержками для сортировки
    for i in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}'
        )
        # Небольшая задержка для обеспечения разного времени создания
        import time
        time.sleep(0.01)
    return news
