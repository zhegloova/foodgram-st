# Foodgram - Итоговый проект

Сервис для публикации рецептов. Позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


### Настройка окружения
1. Клонируйте репозиторий:
```bash
git clone https://github.com/zhegloova/foodgram-project.git
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
```


### Запуск проекта 
1. Запустите docker-compose (из директории infra)
```bash
docker-compose up
```

2. После прогона postman_collection выполните
```bash
docker-compose down -v
```


### API Documentation
API документация (OpenAPI/Swagger) доступна по следующим URL:
- `http://localhost:8000/api/docs/` - Swagger UI


### API Endpoints
- `/api/users/` - управление пользователями
- `/api/recipes/` - управление рецептами
- `/api/ingredients/` - получение списка ингредиентов
- `/api/tags/` - получение списка тегов
