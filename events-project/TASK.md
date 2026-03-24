# Архитектура бэкенда: Платформа рейтинга активности

## 1. Что берёшь на себя (монолит на DRF)

На основе диаграммы из PDF, за вычетом двух микросервисов (Профиль участника и Дашборд «Активности»), твой монолит покрывает:

| Модуль из диаграммы | Django-приложение | Что делает |
|---|---|---|
| Модуль мероприятий | `events` | CRUD мероприятий, призы, подтверждение участия, QR-коды |
| Рейтинговая система | `ratings` | Расчёт рейтинга, таблица лидеров, фильтрация по направлениям |
| Профиль организатора | `organizers` | Публичная страница, счётчик мероприятий, рейтинг доверия |
| Инспектор кадрового резерва | `inspector` | Расширенные фильтры, выгрузка PDF-отчётов |
| Админка (панель управления) | `admin_panel` | Создание мероприятий, модерация организаторов, настройка весов |
| Безопасность / Пользователи | `accounts` | Роли, авторизация, JWT |

---

## 2. Схема базы данных (PostgreSQL)

### Диаграмма связей (текстовая ERD)

```
┌─────────────────────┐
│       User          │
│─────────────────────│
│ id          UUID PK │
│ email       varchar │
│ password    varchar │
│ first_name  varchar │
│ last_name   varchar │
│ role        enum    │──┐  ORGANIZER / PARTICIPANT / OBSERVER / ADMIN
│ city        varchar │  │
│ birth_date  date    │  │
│ avatar      varchar │  │
│ is_verified bool    │  │  (для модерации организаторов)
│ created_at  datetime│  │
└─────────────────────┘  │
         │               │
         │ 1             │
         ▼               │
┌─────────────────────┐  │
│   EventCategory     │  │
│─────────────────────│  │
│ id          UUID PK │  │
│ name        varchar │  │  "IT", "Соц. проектирование", "Медиа"
│ slug        varchar │  │
│ description text    │  │
└─────────────────────┘  │
                         │
┌────────────────────────┘
│
│    ┌─────────────────────────┐
│    │        Event            │
│    │─────────────────────────│
│    │ id              UUID PK │
│    │ organizer_id    UUID FK │──→ User (role=ORGANIZER)
│    │ category_id     UUID FK │──→ EventCategory
│    │ name            varchar │
│    │ description     text    │
│    │ event_date      datetime│
│    │ event_type      enum    │  "LECTURE", "HACKATHON", "FORUM", "VOLUNTEER"...
│    │ difficulty_coef decimal │  коэффициент сложности (1.0 – 3.0)
│    │ base_points     int     │  базовые баллы за участие
│    │ max_participants int    │
│    │ status          enum    │  "DRAFT", "PUBLISHED", "ONGOING", "COMPLETED", "CANCELLED"
│    │ created_at      datetime│
│    └─────────────────────────┘
│              │
│              │ 1
│              ▼
│    ┌─────────────────────────┐
│    │        Prize            │
│    │─────────────────────────│
│    │ id              UUID PK │
│    │ event_id        UUID FK │──→ Event
│    │ name            varchar │  "Мерч", "Билеты на форум", "Стажировка"
│    │ description     text    │
│    │ prize_type      enum    │  "MERCH", "TICKETS", "INTERNSHIP", "GRANT", "MEETING"
│    │ quantity        int     │  сколько штук доступно
│    └─────────────────────────┘
│
│              │
│              ▼
│    ┌──────────────────────────────┐
│    │      Participation           │
│    │──────────────────────────────│
│    │ id              UUID PK      │
│    │ event_id        UUID FK      │──→ Event
│    │ user_id         UUID FK      │──→ User (role=PARTICIPANT)
│    │ status          enum         │  "REGISTERED", "CHECKED_IN", "CONFIRMED", "REJECTED"
│    │ qr_token        varchar      │  уникальный токен для QR-кода
│    │ checked_in_at   datetime     │  когда участник отметился
│    │ confirmed_at    datetime     │  когда организатор подтвердил
│    │ points_awarded  int          │  итоговые начисленные баллы
│    │ created_at      datetime     │
│    │                              │
│    │ UNIQUE(event_id, user_id)    │  один пользователь — одна запись на мероприятие
│    └──────────────────────────────┘
│
│    ┌──────────────────────────────┐
│    │      OrganizerReview         │
│    │──────────────────────────────│
│    │ id              UUID PK      │
│    │ organizer_id    UUID FK      │──→ User (role=ORGANIZER)
│    │ reviewer_id     UUID FK      │──→ User (role=PARTICIPANT)
│    │ event_id        UUID FK      │──→ Event
│    │ score           int          │  1–5
│    │ comment         text         │
│    │ created_at      datetime     │
│    │                              │
│    │ UNIQUE(reviewer_id, event_id)│  один отзыв на мероприятие от участника
│    └──────────────────────────────┘
│
│    ┌──────────────────────────────┐
│    │   RatingSnapshot (опционально)│
│    │──────────────────────────────│
│    │ id              UUID PK      │
│    │ user_id         UUID FK      │──→ User
│    │ rating_it       decimal      │
│    │ rating_social   decimal      │
│    │ rating_media    decimal      │
│    │ common_rating   decimal      │
│    │ rank            int          │  место в общем зачёте
│    │ snapshot_date   date         │  дата снимка (ежедневно/еженедельно)
│    │ created_at      datetime     │
│    └──────────────────────────────┘
│
│    ┌──────────────────────────────┐
│    │   PointWeight (настройка)    │
│    │──────────────────────────────│
│    │ id              UUID PK      │
│    │ event_type      enum         │  тип мероприятия
│    │ category_id     UUID FK      │──→ EventCategory (nullable)
│    │ weight          decimal      │  множитель
│    │ updated_by      UUID FK      │──→ User (ADMIN)
│    │ updated_at      datetime     │
│    └──────────────────────────────┘
```

---

## 3. Формула рейтинга

Рейтинг рассчитывается динамически (или кэшируется в `RatingSnapshot`):

```
common_rating = SUM(
    participation.points_awarded * event.difficulty_coef * point_weight.weight
)
```

Для рейтинга по направлению — та же формула, но фильтр по `event.category`:
- `rating_it` — только `category.slug = "it"`
- `rating_social` — только `category.slug = "social"`
- `rating_media` — только `category.slug = "media"`

---

## 4. Структура Django-проекта

```
parliament_rating/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
│
├── config/                    # Настройки проекта
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py            # Общие настройки
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py                # Корневой роутер
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/              # Пользователи и авторизация
│   │   ├── models.py          # User (кастомный, AbstractUser)
│   │   ├── serializers.py     # Registration, Login, UserProfile
│   │   ├── views.py           # JWT auth endpoints
│   │   ├── permissions.py     # IsOrganizer, IsParticipant, IsObserver, IsAdmin
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── events/                # Мероприятия
│   │   ├── models.py          # Event, EventCategory, Prize, Participation
│   │   ├── serializers.py
│   │   ├── views.py           # CRUD + подтверждение участия + QR
│   │   ├── services.py        # Бизнес-логика (generate_qr, confirm_participation)
│   │   ├── filters.py         # django-filter для фильтрации мероприятий
│   │   ├── urls.py
│   │   └── signals.py         # Пересчёт рейтинга при подтверждении участия
│   │
│   ├── ratings/               # Рейтинговая система
│   │   ├── models.py          # RatingSnapshot, PointWeight
│   │   ├── serializers.py
│   │   ├── views.py           # Leaderboard, filtered ratings
│   │   ├── services.py        # calculate_rating(), rebuild_leaderboard()
│   │   ├── urls.py
│   │   └── management/
│   │       └── commands/
│   │           └── rebuild_ratings.py   # management-команда для пересчёта
│   │
│   ├── organizers/            # Профиль организатора
│   │   ├── serializers.py     # OrganizerPublicProfile, OrganizerReview
│   │   ├── views.py           # Публичная страница, отзывы
│   │   ├── models.py          # OrganizerReview
│   │   └── urls.py
│   │
│   ├── inspector/             # Инспектор кадрового резерва
│   │   ├── serializers.py
│   │   ├── views.py           # Расширенные фильтры, PDF-генерация
│   │   ├── filters.py         # Фильтры по возрасту, городу, баллам
│   │   ├── services.py        # generate_candidate_pdf()
│   │   └── urls.py
│   │
│   └── admin_panel/           # Панель управления
│       ├── serializers.py
│       ├── views.py           # Модерация организаторов, настройка весов
│       └── urls.py
│
└── common/                    # Общие утилиты
    ├── mixins.py              # UUIDMixin, TimestampMixin
    ├── pagination.py          # Стандартная пагинация
    └── renderers.py
```

---

## 5. API-эндпоинты (основные)

### accounts
```
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/              → JWT пара
POST   /api/v1/auth/refresh/
GET    /api/v1/auth/me/                 → текущий пользователь
```

### events
```
GET    /api/v1/events/                  → список мероприятий (с фильтрами)
POST   /api/v1/events/                  → создать (только ORGANIZER/ADMIN)
GET    /api/v1/events/{id}/
PATCH  /api/v1/events/{id}/
DELETE /api/v1/events/{id}/

POST   /api/v1/events/{id}/register/    → участник записывается
POST   /api/v1/events/{id}/checkin/     → участник отмечается (по QR-токену)
POST   /api/v1/events/{id}/confirm/{user_id}/  → организатор подтверждает

GET    /api/v1/events/{id}/participants/
GET    /api/v1/events/{id}/prizes/
POST   /api/v1/events/{id}/prizes/
```

### ratings
```
GET    /api/v1/ratings/leaderboard/                → Топ-100
GET    /api/v1/ratings/leaderboard/?category=it    → по направлению
GET    /api/v1/ratings/user/{user_id}/             → рейтинг конкретного пользователя
```

### organizers
```
GET    /api/v1/organizers/{id}/          → публичный профиль
GET    /api/v1/organizers/{id}/events/   → его мероприятия
GET    /api/v1/organizers/{id}/reviews/  → отзывы
POST   /api/v1/organizers/{id}/reviews/  → оставить отзыв (только PARTICIPANT)
```

### inspector
```
GET    /api/v1/inspector/candidates/     → список с расширенными фильтрами
GET    /api/v1/inspector/candidates/{id}/report/  → скачать PDF
```
Доступ: только `OBSERVER` и `ADMIN`.

### admin_panel
```
GET    /api/v1/admin/organizers/pending/       → список на модерацию
POST   /api/v1/admin/organizers/{id}/approve/
POST   /api/v1/admin/organizers/{id}/reject/
GET    /api/v1/admin/point-weights/
PATCH  /api/v1/admin/point-weights/{id}/
```

---

## 6. Взаимодействие с микросервисами коллеги

Два сервиса коллеги (Профиль участника, Дашборд «Активности») будут потребителями данных из твоего монолита. Схема взаимодействия:

```
┌──────────────────┐        REST API         ┌───────────────────────┐
│  Микросервис:    │ ◄────────────────────── │                       │
│  Профиль         │  GET /api/v1/ratings/   │   Твой монолит (DRF)  │
│  участника       │      user/{id}/         │                       │
│                  │  GET /api/v1/events/    │   - events            │
│  (коллега)       │      ?user_id={id}      │   - ratings           │
└──────────────────┘                         │   - organizers        │
                                             │   - inspector         │
┌──────────────────┐        REST API         │   - admin_panel       │
│  Микросервис:    │ ◄────────────────────── │   - accounts          │
│  Дашборд         │  GET /api/v1/events/    │                       │
│  «Активности»   │      ?status=completed  │                       │
│                  │  GET /api/v1/ratings/   │                       │
│  (коллега)       │      leaderboard/       └───────────────────────┘
└──────────────────┘
```

Твой монолит — **источник правды** (source of truth) для мероприятий, рейтинга и пользователей. Микросервисы коллеги ходят к твоему API за данными.

Что нужно обеспечить:
1. Все ID — UUID (как указано в диаграмме)
2. Эндпоинты для коллеги должны быть задокументированы (drf-spectacular / Swagger)
3. Для аутентификации между сервисами — JWT или service token

---

## 7. Технологический стек

| Компонент | Технология |
|---|---|
| Фреймворк | Django 5.x + Django REST Framework |
| БД | PostgreSQL 16 |
| Авторизация | djangorestframework-simplejwt |
| Фильтрация | django-filter |
| Документация API | drf-spectacular (OpenAPI 3.0 / Swagger) |
| QR-коды | qrcode (Python-библиотека) |
| PDF-отчёты | reportlab или weasyprint |
| Кэш рейтинга | Redis (опционально, для Топ-100) |
| Контейнеризация | Docker + docker-compose |
| Миграции | встроенные Django migrations |

---

## 8. Порядок реализации (что делать по шагам)

**Шаг 1: Каркас проекта**
- `django-admin startproject config .`
- Создать все apps: `accounts`, `events`, `ratings`, `organizers`, `inspector`, `admin_panel`
- Настроить settings (PostgreSQL, JWT, CORS)

**Шаг 2: Модели и миграции (`accounts` + `events`)**
- Кастомный User с ролями
- Event, EventCategory, Prize, Participation
- `python manage.py makemigrations && migrate`

**Шаг 3: Авторизация**
- JWT (register, login, refresh, me)
- Permissions: IsOrganizer, IsParticipant, IsObserver, IsAdmin

**Шаг 4: CRUD мероприятий**
- ViewSet для Event с фильтрами (по категории, дате, статусу)
- Эндпоинты регистрации и подтверждения участия
- Генерация QR-токена при регистрации

**Шаг 5: Рейтинговая система**
- Сервис расчёта рейтинга (в `ratings/services.py`)
- ViewSet для Leaderboard с пагинацией и фильтрацией по категории
- Signal: при `Participation.status → CONFIRMED` — пересчитать рейтинг

**Шаг 6: Профиль организатора**
- Публичный ViewSet (readonly) + отзывы
- Автоподсчёт среднего рейтинга доверия

**Шаг 7: Инспектор кадрового резерва**
- Фильтрация кандидатов (django-filter)
- PDF-генерация отчёта по кандидату

**Шаг 8: Админка (панель управления)**
- Модерация организаторов (approve/reject)
- CRUD для PointWeight

**Шаг 9: Документация и интеграция**
- drf-spectacular → Swagger UI
- Согласовать контракты API с коллегой (для его микросервисов)

**Шаг 10: Docker**
- Dockerfile + docker-compose (Django + PostgreSQL + Redis)