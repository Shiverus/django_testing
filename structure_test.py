import os
import sys
from pathlib import Path
from colorama import init, Fore

init(autoreset=True)


def check_structure():
    """Проверяет структуру проекта согласно требованиям."""

    base_dir = Path(__file__).parent
    print("Проверка структуры проектов...")
    print("=" * 50)

    # Проверяем YaNote
    print("\nПроверка YaNote:")
    print("-" * 30)

    ya_note_path = base_dir / "ya-note "
    notes_path = ya_note_path / "notes"
    tests_path = notes_path / "tests"

    required_ya_note = [
        ya_note_path / "manage.py",
        ya_note_path / "pytest.ini",
        notes_path / "__init__.py",
        notes_path / "admin.py",
        notes_path / "apps.py",
        notes_path / "forms.py",
        notes_path / "models.py",
        notes_path / "urls.py",
        notes_path / "views.py",
        tests_path / "__init__.py",
        tests_path / "test_routes.py",
        tests_path / "test_content.py",
        tests_path / "test_logic.py",
    ]

    for file_path in required_ya_note:
        if file_path.exists():
            print(Fore.GREEN + f"V {file_path.relative_to(base_dir)}")
        else:
            print(Fore.RED
                  + f"X {file_path.relative_to(base_dir)} - ОТСУТСТВУЕТ"
                  )

    # Проверяем YaNews
    print("\nПроверка YaNews:")
    print("-" * 30)

    ya_news_path = base_dir / "ya-news"
    news_path = ya_news_path / "news"
    pytest_tests_path = news_path / "pytest_tests"

    required_ya_news = [
        ya_news_path / "manage.py",
        ya_news_path / "pytest.ini",
        ya_news_path / "README.md",
        news_path / "__init__.py",
        news_path / "admin.py",
        news_path / "apps.py",
        news_path / "forms.py",
        news_path / "models.py",
        news_path / "urls.py",
        news_path / "views.py",
        pytest_tests_path / "__init__.py",
        pytest_tests_path / "conftest.py",
        pytest_tests_path / "test_routes.py",
        pytest_tests_path / "test_content.py",
        pytest_tests_path / "test_logic.py",
    ]

    for file_path in required_ya_news:
        if file_path.exists():
            print(Fore.GREEN + f"V {file_path.relative_to(base_dir)}")
        else:
            print(Fore.RED
                  + f"X {file_path.relative_to(base_dir)} - ОТСУТСТВУЕТ"
                  )

    # Проверяем директории
    print("\nПроверка директорий:")
    print("-" * 30)

    required_dirs = [
        ya_note_path / "templates",
        ya_note_path / "notes" / "migrations",
        ya_news_path / "templates",
        ya_news_path / "news" / "fixtures",
        ya_news_path / "news" / "migrations",
    ]

    for dir_path in required_dirs:
        if dir_path.exists() and dir_path.is_dir():
            print(Fore.GREEN + f"V {dir_path.relative_to(base_dir)}/")
        else:
            print(Fore.RED
                  + f"X {dir_path.relative_to(base_dir)}/ - ОТСУТСТВУЕТ"
                  )

    print("\n" + "=" * 50)
    print("Проверка завершена!")


def run_tests():
    """Запускает тесты обоих проектов."""

    base_dir = Path(__file__).parent
    print("\nЗапуск тестов...")
    print("=" * 50)

    # Запуск тестов YaNote
    print("\nТесты YaNote (unittest):")
    print("-" * 30)

    ya_note_path = base_dir / "ya-note"
    if (ya_note_path / "manage.py").exists():
        os.chdir(ya_note_path)
        os.system("python manage.py test notes.tests --verbosity=2")
    else:
        print("Файл manage.py не найден!")

    # Запуск тестов YaNews
    print("\nТесты YaNews (pytest):")
    print("-" * 30)

    ya_news_path = base_dir / "ya-news"
    if (ya_news_path / "pytest.ini").exists():
        os.chdir(ya_news_path)
        os.system("pytest news/pytest_tests/ -v")
    else:
        print("Файл pytest.ini не найден!")

    os.chdir(base_dir)


if __name__ == "__main__":
    check_structure()
