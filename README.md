# Razum More Hack

[![Lint](https://github.com/viktorgezz/razum-more-hack/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/viktorgezz/razum-more-hack/actions/workflows/lint.yml)
[![CI](https://img.shields.io/github/checks-status/viktorgezz/razum-more-hack/main?label=CI&logo=githubactions&logoColor=white)](https://github.com/viktorgezz/razum-more-hack/actions)
[![Docker](https://img.shields.io/badge/Docker-events--project-2496ED?logo=docker&logoColor=white)](https://github.com/viktorgezz/razum-more-hack/blob/main/events-project/Dockerfile)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-REST-ff1709?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![JWT](https://img.shields.io/badge/JWT-simplejwt-000000?logo=jsonwebtokens&logoColor=white)](https://django-rest-framework-simplejwt.readthedocs.io/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-Swagger-85EA2D?logo=swagger&logoColor=black)](https://swagger.io/)

## Описание

Монорепозиторий веб-платформы для учёта активности участников молодёжного парламента и кадрового резерва: мероприятия, прозрачный рейтинг, профили организаторов и участников, инструменты для кадровой службы (инспектор, отчёты PDF) и админ-панель.

**Backend** — Django REST Framework, JWT, OpenAPI (Swagger/ReDoc). **Frontend** — Next.js с обращением к REST API.

## Запуск проекта (Docker)

Самый быстрый способ развернуть весь проект целиком — использовать Docker Compose.

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/viktorgezz/razum-more-hack.git
   cd razum-more-hack
   ```

2. **Настройте переменные окружения (.env):**

   Скопируйте пример файла конфигурации:

   ```bash
   cp events-project/.env.example events-project/.env
   ```

   *По умолчанию настройки из примера подходят для локального запуска фронтенда (CORS разрешен для `http://localhost:3000`).*

3. **Запустите контейнеры:**

   ```bash
   docker compose up -d --build
   ```

После окончания сборки:

- **Frontend:** <http://localhost:3000>
- **Backend API:** <http://localhost:8000>
- **API Документация (Swagger):** <http://localhost:8000/api/docs/>

## Аккаунты по которым можно зайти и проверить работаспособность

Аккаунты:

- admin/admin123
- org_ivanova/org123
-org_petrov/org123
- участники smirnov_alex
- kozlova_maria / ... все с паролем user123
- наблюдатель observer_hr/obs123.

## Схема проекта

```mermaid
flowchart TB
    subgraph client["Клиент"]
        Browser["Браузер"]
    end

    subgraph fe["frontend/"]
        Next["Next.js + React + TS"]
    end

    subgraph api["events-project — Django"]
        DRF["Django REST Framework"]
        subgraph apps["Приложения"]
            ACC["accounts — auth JWT"]
            EVT["events — мероприятия"]
            ORG["organizers — профили"]
            RTG["rating — лидерборд"]
            INS["inspector — кадры"]
            ADM["admin_panel — модерация"]
        end
        DRF --> ACC & EVT & ORG & RTG & INS & ADM
    end

    subgraph data["Данные"]
        DB[("SQLite / PostgreSQL")]
    end

    Browser --> Next
    Next -->|"HTTPS REST + JWT"| DRF
    ACC & EVT & ORG & RTG & INS & ADM --> DB
```

## Инструкция

### Backend (API)

```bash
cd events-project
python -m pip install -r requirements.txt
```

При конфликте истории миграций удалите локальный файл `events-project/db.sqlite3` и выполните `migrate` заново.

```bash
python manage.py migrate
python manage.py runserver
```

### Frontend (опционально)

```bash
cd frontend
npm install
npm run dev
```

### Аутентификация

Защищённые эндпоинты требуют JWT:

- `POST /api/token/` — выдача токенов  
- `POST /api/token/refresh/` — обновление  

Заголовок запросов:

```text
Authorization: Bearer <access_token>
```

### Документация API

| Ресурс | URL (локально) |
|--------|----------------|
| Swagger UI | <http://127.0.0.1:8000/api/docs/> |
| ReDoc | <http://127.0.0.1:8000/api/redoc/> |
| OpenAPI schema | <http://127.0.0.1:8000/api/schema/> |
| Файл схемы | `events-project/openapi.yaml` |

### Проверка кода и тесты (как в CI)

```bash
cd events-project
ruff check . --select E9,F63,F7,F82
python manage.py test
python manage.py check
python manage.py spectacular --file openapi.yaml --validate
```

### Модули backend

| Папка | Назначение |
|-------|------------|
| `accounts` | Регистрация, JWT, профиль |
| `events` | Мероприятия, призы, регистрация, чекин, подтверждение |
| `organizers` | Публичные профили организаторов и отзывы |
| `rating` | Лидерборд, рейтинги, веса баллов |
| `inspector` | Фильтры кандидатов, PDF-отчёты |
| `admin_panel` | Модерация организаторов, веса (через `rating`) |

---

Плашки **Lint** и **Tests** — официальные бейджи workflow; **CI** — общий статус проверок на ветке `main` (shields.io). Плашка **Docker** ведёт на [`events-project/Dockerfile`](events-project/Dockerfile).
