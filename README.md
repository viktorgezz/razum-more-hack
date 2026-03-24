# Razum More Hack

Монолитный backend на Django REST Framework для платформы рейтинга активности молодежного парламента и кадрового резерва.

## Что есть в проекте

- `events` - мероприятия, призы, регистрация, чекин и подтверждение участия
- `organizers` - публичные профили организаторов и отзывы
- `rating` - лидерборд, рейтинги участников и веса баллов
- `inspector` - кадровый инспектор, фильтры кандидатов и PDF-отчеты

## Стек

- Python 3.13
- Django 5
- Django REST Framework
- JWT (`simplejwt`)
- OpenAPI / Swagger (`drf-spectacular`)
- SQLite по умолчанию

## Установка

```powershell
cd events-project
python -m pip install -r requirements.txt
```

## Запуск

Если в локальной `db.sqlite3` осталась старая несовместимая история миграций после мерджа веток, используйте отдельный sqlite-файл:

```powershell
$env:SQLITE_DB_NAME="clean.sqlite3"
python manage.py migrate
python manage.py runserver
```

Если база новая и чистая, достаточно обычного запуска:

```powershell
cd events-project
python manage.py migrate
python manage.py runserver
```

## Аутентификация

Все защищенные эндпоинты работают через JWT:

- `POST /api/token/`
- `POST /api/token/refresh/`

Заголовок для запросов:

```text
Authorization: Bearer <access_token>
```

## Документация API

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI schema endpoint: `http://127.0.0.1:8000/api/schema/`
- Сгенерированный файл схемы: `events-project/openapi.yaml`

## Проверка

```powershell
cd events-project
$env:SQLITE_DB_NAME="clean.sqlite3"
python manage.py check
python manage.py test
python manage.py spectacular --file openapi.yaml --validate
```
