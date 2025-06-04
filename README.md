# Foodgram - Продуктовый помощник

Сервис для публикации рецептов. Позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Разработка

### Требования

- Python 3.9+
- Django 4.2
- Docker
- Docker Compose

### Настройка окружения

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/foodgram-project.git
cd foodgram-project
```

2. Создайте файл `.env` в корневой директории проекта:
```env
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
DB_USER=foodgram_user
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Email settings (опционально)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Запуск проекта

1. Запустите Docker Compose:
```bash
docker-compose up -d --build
```

2. Примените миграции:
```bash
docker-compose exec backend python manage.py migrate
```

3. Создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

4. Загрузите начальные данные (ингредиенты):
```bash
docker-compose exec backend python manage.py import_ingredients
```

### Тестовые пользователи

После запуска проекта вы можете использовать следующие тестовые учетные записи:

1. Администратор:
- Email: admin@foodgram.com
- Пароль: admin

2. Тестовый пользователь:
- Email: user@foodgram.com
- Пароль: user12345

Или создайте нового пользователя через API или административный интерфейс.

### API Documentation

API документация (OpenAPI/Swagger) доступна по следующим URL:
- `http://localhost:8000/api/docs/` - Swagger UI
- `http://localhost:8000/api/docs/redoc/` - ReDoc

### Разработка

1. Запуск сервера для разработки:
```bash
python manage.py runserver
```

2. Запуск тестов:
```bash
python manage.py test
```

3. Проверка кода:
```bash
flake8 .
black .
isort .
```

### API Endpoints

Основные эндпоинты API:

- `/api/users/` - управление пользователями
- `/api/recipes/` - управление рецептами
- `/api/ingredients/` - получение списка ингредиентов
- `/api/tags/` - получение списка тегов

Полный список эндпоинтов и их описание доступны в документации API.

### Дополнительные команды

1. Создание новых миграций:
```bash
python manage.py makemigrations
```

2. Сброс базы данных:
```bash
python manage.py flush
```

3. Сбор статических файлов:
```bash
python manage.py collectstatic
```

## Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

