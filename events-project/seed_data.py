# -*- coding: utf-8 -*-
"""
\u041f\u043e\u043b\u043d\u044b\u0439 \u0441\u0431\u0440\u043e\u0441 \u0438 \u043f\u0435\u0440\u0435\u0441\u0435\u0432 \u0442\u0435\u0441\u0442\u043e\u0432\u044b\u0445 \u0434\u0430\u043d\u043d\u044b\u0445.
\u0417\u0430\u043f\u0443\u0441\u043a: python seed_data.py
"""
import os
import sys
import secrets
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "events-project.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from events.models import Event, EventCategory, Participation, Prize
from rating.models import PointWeight, RatingSnapshot
from rating.services import rebuild_leaderboard

User = get_user_model()

# ─────────────────────────────────────────────
# 0. \u041f\u043e\u043b\u043d\u0430\u044f \u043e\u0447\u0438\u0441\u0442\u043a\u0430
# ─────────────────────────────────────────────
print("\u041e\u0447\u0438\u0441\u0442\u043a\u0430 \u0411\u0414...")
RatingSnapshot.objects.all().delete()
Participation.objects.all().delete()
Prize.objects.all().delete()
Event.objects.all().delete()
EventCategory.objects.all().delete()
PointWeight.objects.all().delete()
User.objects.all().delete()

# ─────────────────────────────────────────────
# 1. \u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440
# ─────────────────────────────────────────────
print("\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439...")
admin = User.objects.create_superuser(
    username="admin",
    password="admin123",
    email="admin@activemind.ru",
    first_name="\u0410\u043b\u0435\u043a\u0441\u0430\u043d\u0434\u0440",
    last_name="\u041f\u043e\u043f\u043e\u0432",
    role=User.Role.ADMIN,
    is_verified=True,
    city="\u041c\u043e\u0441\u043a\u0432\u0430",
)

# ─────────────────────────────────────────────
# 2. \u041e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0442\u043e\u0440\u044b
# ─────────────────────────────────────────────
org1 = User.objects.create_user(
    username="org_ivanova",
    password="org123",
    email="ivanova@activemind.ru",
    first_name="\u0415\u043a\u0430\u0442\u0435\u0440\u0438\u043d\u0430",
    last_name="\u0418\u0432\u0430\u043d\u043e\u0432\u0430",
    role=User.Role.ORGANIZER,
    is_verified=True,
    city="\u041c\u043e\u0441\u043a\u0432\u0430",
)
org2 = User.objects.create_user(
    username="org_petrov",
    password="org123",
    email="petrov@activemind.ru",
    first_name="\u0414\u043c\u0438\u0442\u0440\u0438\u0439",
    last_name="\u041f\u0435\u0442\u0440\u043e\u0432",
    role=User.Role.ORGANIZER,
    is_verified=True,
    city="\u0421\u0430\u043d\u043a\u0442-\u041f\u0435\u0442\u0435\u0440\u0431\u0443\u0440\u0433",
)

# ─────────────────────────────────────────────
# 3. \u0423\u0447\u0430\u0441\u0442\u043d\u0438\u043a\u0438
# ─────────────────────────────────────────────
PART_DATA = [
    ("smirnov_alex",    "\u0410\u043b\u0435\u043a\u0441\u0435\u0439",       "\u0421\u043c\u0438\u0440\u043d\u043e\u0432",       "\u041c\u043e\u0441\u043a\u0432\u0430"),
    ("kozlova_maria",   "\u041c\u0430\u0440\u0438\u044f",        "\u041a\u043e\u0437\u043b\u043e\u0432\u0430",       "\u041a\u0430\u0437\u0430\u043d\u044c"),
    ("fedorova_anna",   "\u0410\u043d\u043d\u0430",         "\u0424\u0451\u0434\u043e\u0440\u043e\u0432\u0430",      "\u0415\u043a\u0430\u0442\u0435\u0440\u0438\u043d\u0431\u0443\u0440\u0433"),
    ("nikitin_igor",    "\u0418\u0433\u043e\u0440\u044c",        "\u041d\u0438\u043a\u0438\u0442\u0438\u043d",       "\u041d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a"),
    ("sorokina_kate",   "\u0415\u043a\u0430\u0442\u0435\u0440\u0438\u043d\u0430",     "\u0421\u043e\u0440\u043e\u043a\u0438\u043d\u0430",     "\u0421\u0430\u043c\u0430\u0440\u0430"),
    ("morozov_pavel",   "\u041f\u0430\u0432\u0435\u043b",        "\u041c\u043e\u0440\u043e\u0437\u043e\u0432",       "\u041d\u0438\u0436\u043d\u0438\u0439 \u041d\u043e\u0432\u0433\u043e\u0440\u043e\u0434"),
    ("volkova_elena",   "\u0415\u043b\u0435\u043d\u0430",        "\u0412\u043e\u043b\u043a\u043e\u0432\u0430",       "\u0423\u0444\u0430"),
]
participants = []
for username, first, last, city in PART_DATA:
    u = User.objects.create_user(
        username=username,
        password="user123",
        email=f"{username}@activemind.ru",
        first_name=first,
        last_name=last,
        role=User.Role.PARTICIPANT,
        is_verified=True,
        city=city,
    )
    participants.append(u)

# \u041d\u0430\u0431\u043b\u044e\u0434\u0430\u0442\u0435\u043b\u044c
observer = User.objects.create_user(
    username="observer_hr",
    password="obs123",
    email="hr@activemind.ru",
    first_name="\u041d\u0430\u0442\u0430\u043b\u044c\u044f",
    last_name="\u0421\u0435\u0440\u0433\u0435\u0435\u0432\u0430",
    role=User.Role.OBSERVER,
    is_verified=True,
    city="\u041c\u043e\u0441\u043a\u0432\u0430",
)

# ─────────────────────────────────────────────
# 4. \u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438
# ─────────────────────────────────────────────
print("\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439...")
cat_it = EventCategory.objects.create(
    name="IT-\u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438",
    slug="it",
    description="\u041c\u0435\u0440\u043e\u043f\u0440\u0438\u044f\u0442\u0438\u044f \u0432 \u0441\u0444\u0435\u0440\u0435 \u0446\u0438\u0444\u0440\u043e\u0432\u044b\u0445 \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0439",
)
cat_social = EventCategory.objects.create(
    name="\u0421\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u044b",
    slug="social",
    description="\u0412\u043e\u043b\u043e\u043d\u0442\u0451\u0440\u0441\u0442\u0432\u043e, \u0431\u043b\u0430\u0433\u043e\u0442\u0432\u043e\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0435 \u0430\u043a\u0446\u0438\u0438",
)
cat_media = EventCategory.objects.create(
    name="\u041c\u0435\u0434\u0438\u0430 \u0438 \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438",
    slug="media",
    description="\u041f\u0440\u0435\u0441\u0441-\u043a\u043e\u043d\u0444\u0435\u0440\u0435\u043d\u0446\u0438\u0438, \u043c\u0435\u0434\u0438\u0430\u0444\u043e\u0440\u0443\u043c\u044b, \u0436\u0443\u0440\u043d\u0430\u043b\u0438\u0441\u0442\u0438\u043a\u0430",
)

# ─────────────────────────────────────────────
# 5. \u0412\u0435\u0441\u0430 \u0431\u0430\u043b\u043b\u043e\u0432
# ─────────────────────────────────────────────
print("\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0432\u0435\u0441\u043e\u0432 \u0431\u0430\u043b\u043b\u043e\u0432...")
for et in ["LECTURE", "HACKATHON", "FORUM", "VOLUNTEER"]:
    w = Decimal("1.5") if et == "HACKATHON" else Decimal("1.0")
    for cat in [cat_it, cat_social, cat_media, None]:
        PointWeight.objects.create(
            event_type=et,
            category=cat,
            weight=w,
            updated_by=admin,
        )

# ─────────────────────────────────────────────
# 6. \u041c\u0435\u0440\u043e\u043f\u0440\u0438\u044f\u0442\u0438\u044f
# ─────────────────────────────────────────────
print("\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043c\u0435\u0440\u043e\u043f\u0440\u0438\u044f\u0442\u0438\u0439...")
now = timezone.now()

# --- \u0417\u0410\u0412\u0415\u0420\u0428\u0418\u041b\u0418\u0421\u042c ---
ev1 = Event.objects.create(
    organizer=org1, category=cat_it,
    name="\u0425\u0430\u043a\u0430\u0442\u043e\u043d \u00ab\u0426\u0438\u0444\u0440\u043e\u0432\u043e\u0439 \u0433\u043e\u0440\u043e\u0434\u00bb",
    description="\u0421\u043e\u0440\u0435\u0432\u043d\u043e\u0432\u0430\u043d\u0438\u0435 \u043f\u043e \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0435 \u0446\u0438\u0444\u0440\u043e\u0432\u044b\u0445 \u0440\u0435\u0448\u0435\u043d\u0438\u0439 \u0434\u043b\u044f \u0433\u043e\u0440\u043e\u0434\u0441\u043a\u043e\u0439 \u0438\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u044b. 24 \u0447\u0430\u0441\u0430 \u0438\u043d\u0442\u0435\u043d\u0441\u0438\u0432\u043d\u043e\u0439 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438.",
    event_date=now - datetime.timedelta(days=30),
    event_type="HACKATHON", difficulty_coef=Decimal("1.50"),
    base_points=100, max_participants=50, status="COMPLETED",
)
ev2 = Event.objects.create(
    organizer=org1, category=cat_social,
    name="\u0424\u043e\u0440\u0443\u043c \u043c\u043e\u043b\u043e\u0434\u0451\u0436\u043d\u044b\u0445 \u043b\u0438\u0434\u0435\u0440\u043e\u0432",
    description="\u0415\u0436\u0435\u0433\u043e\u0434\u043d\u044b\u0439 \u0444\u043e\u0440\u0443\u043c, \u043f\u043e\u0441\u0432\u044f\u0449\u0451\u043d\u043d\u044b\u0439 \u0440\u0430\u0437\u0432\u0438\u0442\u0438\u044e \u043b\u0438\u0434\u0435\u0440\u0441\u043a\u0438\u0445 \u043a\u0430\u0447\u0435\u0441\u0442\u0432 \u0438 \u0441\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u043c \u043f\u0440\u043e\u0435\u043a\u0442\u0430\u043c.",
    event_date=now - datetime.timedelta(days=20),
    event_type="FORUM", difficulty_coef=Decimal("1.20"),
    base_points=80, max_participants=200, status="COMPLETED",
)
ev3 = Event.objects.create(
    organizer=org2, category=cat_media,
    name="\u0428\u043a\u043e\u043b\u0430 \u043c\u0435\u0434\u0438\u0430\u0433\u0440\u0430\u043c\u043e\u0442\u043d\u043e\u0441\u0442\u0438",
    description="\u041f\u0440\u0430\u043a\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043a\u0443\u0440\u0441 \u043f\u043e \u0440\u0430\u0431\u043e\u0442\u0435 \u0441 \u0421\u041c\u0418: \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0438, \u0441\u044a\u0451\u043c\u043a\u0430, \u043c\u043e\u043d\u0442\u0430\u0436.",
    event_date=now - datetime.timedelta(days=15),
    event_type="LECTURE", difficulty_coef=Decimal("1.00"),
    base_points=60, max_participants=30, status="COMPLETED",
)
ev4 = Event.objects.create(
    organizer=org2, category=cat_social,
    name="\u0412\u043e\u043b\u043e\u043d\u0442\u0451\u0440\u0441\u043a\u0430\u044f \u0430\u043a\u0446\u0438\u044f \u00ab\u0427\u0438\u0441\u0442\u044b\u0439 \u0431\u0435\u0440\u0435\u0433\u00bb",
    description="\u0415\u0436\u0435\u0433\u043e\u0434\u043d\u0430\u044f \u044d\u043a\u043e\u043b\u043e\u0433\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0430\u043a\u0446\u0438\u044f \u043f\u043e \u043e\u0447\u0438\u0441\u0442\u043a\u0435 \u043f\u0430\u0440\u043a\u043e\u0432\u044b\u0445 \u0437\u043e\u043d \u0438 \u043d\u0430\u0431\u0435\u0440\u0435\u0436\u043d\u044b\u0445 \u0442\u0435\u0440\u0440\u0438\u0442\u043e\u0440\u0438\u0439.",
    event_date=now - datetime.timedelta(days=7),
    event_type="VOLUNTEER", difficulty_coef=Decimal("1.00"),
    base_points=40, max_participants=100, status="COMPLETED",
)

# --- \u0418\u0414\u0401\u0422 \u0421\u0415\u0419\u0427\u0410\u0421 ---
ev5 = Event.objects.create(
    organizer=org1, category=cat_it,
    name="\u041c\u0430\u0441\u0442\u0435\u0440-\u043a\u043b\u0430\u0441\u0441 \u043f\u043e Python",
    description="\u0418\u043d\u0442\u0435\u043d\u0441\u0438\u0432\u043d\u044b\u0439 \u043c\u0430\u0441\u0442\u0435\u0440-\u043a\u043b\u0430\u0441\u0441 \u0434\u043b\u044f \u043d\u0430\u0447\u0438\u043d\u0430\u044e\u0449\u0438\u0445 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a\u043e\u0432. \u041e\u0441\u043d\u043e\u0432\u044b, \u0432\u0435\u0431-\u0444\u0440\u0435\u0439\u043c\u0432\u043e\u0440\u043a\u0438, \u043f\u0440\u0430\u043a\u0442\u0438\u043a\u0443\u043c.",
    event_date=now + datetime.timedelta(hours=2),
    event_type="LECTURE", difficulty_coef=Decimal("1.10"),
    base_points=50, max_participants=40, status="ONGOING",
)

# --- \u041f\u0420\u0415\u0414\u0421\u0422\u041e\u042f\u0429\u0418\u0415 ---
ev6 = Event.objects.create(
    organizer=org2, category=cat_it,
    name="\u0425\u0430\u043a\u0430\u0442\u043e\u043d \u00ab\u0418\u043d\u043d\u043e\u0432\u0430\u0446\u0438\u0438 \u0432 \u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0438\u00bb",
    description="\u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435 \u0446\u0438\u0444\u0440\u043e\u0432\u043e\u0439 \u043f\u0440\u043e\u0434\u0443\u043a\u0442 \u0434\u043b\u044f \u0441\u0438\u0441\u0442\u0435\u043c\u044b \u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u044f. 24 \u0447\u0430\u0441\u0430, \u043a\u043e\u043c\u0430\u043d\u0434\u044b \u0434\u043e 4 \u0447\u0435\u043b\u043e\u0432\u0435\u043a.",
    event_date=now + datetime.timedelta(days=10),
    event_type="HACKATHON", difficulty_coef=Decimal("1.50"),
    base_points=120, max_participants=60, status="PUBLISHED",
)
ev7 = Event.objects.create(
    organizer=org1, category=cat_social,
    name="\u041a\u0432\u0435\u0441\u0442-\u0438\u0433\u0440\u0430 \u00ab\u0414\u043e\u0431\u0440\u044b\u0435 \u0434\u0435\u043b\u0430\u00bb",
    description="\u0413\u043e\u0440\u043e\u0434\u0441\u043a\u0430\u044f \u043a\u0432\u0435\u0441\u0442-\u0438\u0433\u0440\u0430, \u043f\u043e\u0441\u0432\u044f\u0449\u0451\u043d\u043d\u0430\u044f \u0441\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u043c\u0443 \u043f\u0440\u0435\u0434\u043f\u0440\u0438\u043d\u0438\u043c\u0430\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u0443 \u0438 \u0431\u043b\u0430\u0433\u043e\u0442\u0432\u043e\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u043c \u043f\u0440\u043e\u0435\u043a\u0442\u0430\u043c.",
    event_date=now + datetime.timedelta(days=14),
    event_type="OTHER", difficulty_coef=Decimal("1.00"),
    base_points=45, max_participants=80, status="PUBLISHED",
)
ev8 = Event.objects.create(
    organizer=org2, category=cat_media,
    name="\u041c\u0435\u0434\u0438\u0430\u0444\u043e\u0440\u0443\u043c \u00ab\u0413\u043e\u043b\u043e\u0441 \u043c\u043e\u043b\u043e\u0434\u0451\u0436\u0438\u00bb",
    description="\u041e\u0431\u0449\u0435\u0440\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0438\u0439 \u043c\u0435\u0434\u0438\u0430\u0444\u043e\u0440\u0443\u043c \u0441 \u0443\u0447\u0430\u0441\u0442\u0438\u0435\u043c \u0436\u0443\u0440\u043d\u0430\u043b\u0438\u0441\u0442\u043e\u0432, \u0431\u043b\u043e\u0433\u0435\u0440\u043e\u0432 \u0438 \u043a\u043e\u043d\u0442\u0435\u043d\u0442-\u043c\u0435\u0439\u043a\u0435\u0440\u043e\u0432.",
    event_date=now + datetime.timedelta(days=21),
    event_type="FORUM", difficulty_coef=Decimal("1.20"),
    base_points=70, max_participants=150, status="PUBLISHED",
)

# --- \u0427\u0415\u0420\u041d\u041e\u0412\u0418\u041a ---
ev9 = Event.objects.create(
    organizer=org1, category=cat_it,
    name="\u0412\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0432 \u0438\u0441\u043a\u0443\u0441\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0438\u043d\u0442\u0435\u043b\u043b\u0435\u043a\u0442",
    description="\u0412\u0432\u043e\u0434\u043d\u044b\u0439 \u043a\u0443\u0440\u0441 \u043f\u043e \u043c\u0430\u0448\u0438\u043d\u043d\u043e\u043c\u0443 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u044e \u0438 \u043d\u0435\u0439\u0440\u043e\u0441\u0435\u0442\u044f\u043c.",
    event_date=now + datetime.timedelta(days=45),
    event_type="LECTURE", difficulty_coef=Decimal("1.00"),
    base_points=55, max_participants=25, status="DRAFT",
)

# ─────────────────────────────────────────────
# 7. \u041f\u0440\u0438\u0437\u044b
# ─────────────────────────────────────────────
print("\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u0440\u0438\u0437\u043e\u0432...")
Prize.objects.create(event=ev1, name="\u0413\u0440\u0430\u043d\u0442 \u043d\u0430 \u0441\u0442\u0430\u0440\u0442\u0430\u043f", prize_type="GRANT", quantity=1,
    description="\u0413\u0440\u0430\u043d\u0442 500\u00a0000 \u0440\u0443\u0431. \u0434\u043b\u044f \u043b\u0443\u0447\u0448\u0435\u0439 \u043a\u043e\u043c\u0430\u043d\u0434\u044b")
Prize.objects.create(event=ev1, name="\u041c\u0435\u0440\u0447 \u00ab\u0410\u043a\u0442\u0438\u0432\u043d\u044b\u0439 \u0440\u0430\u0437\u0443\u043c\u00bb", prize_type="MERCH", quantity=3,
    description="\u0424\u0443\u0442\u0431\u043e\u043b\u043a\u0430, \u043a\u0440\u044e\u0447\u043a\u0430, \u043d\u043e\u0443\u0442\u0431\u0443\u043a")
Prize.objects.create(event=ev2, name="\u0421\u0442\u0430\u0436\u0438\u0440\u043e\u0432\u043a\u0430 \u0432 \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438 \u0433\u043e\u0440\u043e\u0434\u0430", prize_type="INTERNSHIP", quantity=2,
    description="\u041e\u043f\u043b\u0430\u0447\u0438\u0432\u0430\u0435\u043c\u0430\u044f \u0441\u0442\u0430\u0436\u0438\u0440\u043e\u0432\u043a\u0430 3 \u043c\u0435\u0441\u044f\u0446\u0430")
Prize.objects.create(event=ev3, name="\u0411\u0438\u043b\u0435\u0442\u044b \u043d\u0430 \u0444\u0435\u0441\u0442\u0438\u0432\u0430\u043b\u044c", prize_type="TICKETS", quantity=5,
    description="\u0411\u0438\u043b\u0435\u0442\u044b \u043d\u0430 \u041c\u0435\u0434\u0438\u0430\u0444\u0435\u0441\u0442 2025")
Prize.objects.create(event=ev6, name="\u0413\u0440\u0430\u043d\u0442 \u043d\u0430 \u0440\u0430\u0437\u0432\u0438\u0442\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u0430", prize_type="GRANT", quantity=1,
    description="\u0413\u0440\u0430\u043d\u0442 300\u00a0000 \u0440\u0443\u0431. \u0434\u043b\u044f \u043f\u043e\u0431\u0435\u0434\u0438\u0442\u0435\u043b\u044f")
Prize.objects.create(event=ev8, name="\u0412\u0441\u0442\u0440\u0435\u0447\u0430 \u0441 \u0440\u0435\u0434\u0430\u043a\u0446\u0438\u0435\u0439 \u0444\u0435\u0434\u0435\u0440\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u0438\u0437\u0434\u0430\u043d\u0438\u044f", prize_type="MEETING", quantity=3,
    description="\u041b\u0438\u0447\u043d\u0430\u044f \u0432\u0441\u0442\u0440\u0435\u0447\u0430 \u0441 \u0433\u043b\u0430\u0432\u043d\u044b\u043c \u0440\u0435\u0434\u0430\u043a\u0442\u043e\u0440\u043e\u043c")

# ─────────────────────────────────────────────
# 8. \u0423\u0447\u0430\u0441\u0442\u0438\u044f
# ─────────────────────────────────────────────
print("\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0443\u0447\u0430\u0441\u0442\u0438\u0439...")
conf_check = now - datetime.timedelta(days=29, hours=1)
conf_time  = now - datetime.timedelta(days=29)

def make_part(event, user, status, points, checked_at=None, confirmed_at=None):
    return Participation.objects.create(
        event=event,
        user=user,
        status=status,
        qr_token=f"qr-{user.username}-{event.id}-{secrets.token_urlsafe(8)}",
        points_awarded=points,
        checked_in_at=checked_at,
        confirmed_at=confirmed_at,
    )

# ev1 \u2014 \u0425\u0430\u043a\u0430\u0442\u043e\u043d (IT, HACKATHON, base=100, coef=1.5, weight=1.5)
# \u0440\u0435\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0435\u0439\u0442\u0438\u043d\u0433: 100 * 1.5 * 1.5 = 225
make_part(ev1, participants[0], "CONFIRMED", 100, conf_check, conf_time)   # smirnov_alex
make_part(ev1, participants[1], "CONFIRMED",  80, conf_check, conf_time)   # kozlova_maria
make_part(ev1, participants[3], "CONFIRMED",  70, conf_check, conf_time)   # nikitin_igor
make_part(ev1, participants[4], "CONFIRMED",  60, conf_check, conf_time)   # sorokina_kate
make_part(ev1, participants[2], "REJECTED",    0)                          # fedorova_anna

# ev2 \u2014 \u0424\u043e\u0440\u0443\u043c (social, FORUM, base=80, coef=1.2, weight=1.0)
make_part(ev2, participants[0], "CONFIRMED", 80, conf_check, conf_time)
make_part(ev2, participants[1], "CONFIRMED", 80, conf_check, conf_time)
make_part(ev2, participants[2], "CONFIRMED", 80, conf_check, conf_time)
make_part(ev2, participants[5], "CONFIRMED", 80, conf_check, conf_time)
make_part(ev2, participants[6], "CONFIRMED", 80, conf_check, conf_time)

# ev3 \u2014 \u0428\u043a\u043e\u043b\u0430 \u043c\u0435\u0434\u0438\u0430 (media, LECTURE, base=60, coef=1.0, weight=1.0)
make_part(ev3, participants[0], "CONFIRMED", 60, conf_check, conf_time)
make_part(ev3, participants[2], "CONFIRMED", 60, conf_check, conf_time)
make_part(ev3, participants[4], "CONFIRMED", 60, conf_check, conf_time)
make_part(ev3, participants[6], "CONFIRMED", 60, conf_check, conf_time)

# ev4 \u2014 \u0412\u043e\u043b\u043e\u043d\u0442\u0451\u0440\u0441\u0442\u0432\u043e (social, VOLUNTEER, base=40, coef=1.0, weight=1.0)
make_part(ev4, participants[1], "CONFIRMED", 40, conf_check, conf_time)
make_part(ev4, participants[2], "CONFIRMED", 40, conf_check, conf_time)
make_part(ev4, participants[3], "CONFIRMED", 40, conf_check, conf_time)
make_part(ev4, participants[5], "CONFIRMED", 40, conf_check, conf_time)

# ev5 \u2014 \u041e\u043d\u0433\u043e\u0438\u043d\u0433: \u0447\u0430\u0441\u0442\u044c \u043e\u0442\u043c\u0435\u0447\u0435\u043d\u0430
make_part(ev5, participants[0], "CHECKED_IN", 0, checked_at=now - datetime.timedelta(minutes=30))
make_part(ev5, participants[1], "CHECKED_IN", 0, checked_at=now - datetime.timedelta(minutes=20))
make_part(ev5, participants[3], "REGISTERED", 0)
make_part(ev5, participants[5], "REGISTERED", 0)

# ev6, ev7, ev8 \u2014 \u0431\u0443\u0434\u0443\u0449\u0438\u0435: REGISTERED
for ev, plist in [
    (ev6, [participants[0], participants[1], participants[2], participants[3]]),
    (ev7, [participants[2], participants[3], participants[4], participants[5]]),
    (ev8, [participants[1], participants[2], participants[4], participants[6]]),
]:
    for p in plist:
        make_part(ev, p, "REGISTERED", 0)

# ─────────────────────────────────────────────
# 9. \u041f\u0435\u0440\u0435\u0441\u0447\u0451\u0442 \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0430
# ─────────────────────────────────────────────
print("\u041f\u0435\u0440\u0435\u0441\u0447\u0451\u0442 \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0430...")
rebuild_leaderboard()

# ─────────────────────────────────────────────
# \u0418\u0442\u043e\u0433\u0438
# ─────────────────────────────────────────────
print()
print("=" * 55)
print("  \u0411\u0410\u0417\u0410 \u0414\u0410\u041d\u041d\u042b\u0425 \u0423\u0421\u041f\u0415\u0428\u041d\u041e \u0417\u0410\u041f\u041e\u041b\u041d\u0415\u041d\u0410")
print("=" * 55)
print(f"  \u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439:     {User.objects.count()}")
print(f"  \u041c\u0435\u0440\u043e\u043f\u0440\u0438\u044f\u0442\u0438\u0439:      {Event.objects.count()} (4 \u0437\u0430\u0432\u0435\u0440\u0448., 1 \u0438\u0434\u0451\u0442, 3 \u043f\u0440\u0435\u0434\u0441\u0442., 1 \u0447\u0435\u0440\u043d.)")
print(f"  \u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439:       {EventCategory.objects.count()}")
print(f"  \u0423\u0447\u0430\u0441\u0442\u0438\u0439:         {Participation.objects.count()}")
print(f"  \u041f\u0440\u0438\u0437\u043e\u0432:           {Prize.objects.count()}")
print(f"  \u0421\u043d\u0438\u043c\u043a\u043e\u0432 \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0430: {RatingSnapshot.objects.count()}")
print("=" * 55)
print()
print("\u0410\u041a\u041a\u0410\u0423\u041d\u0422\u042b \u0414\u041b\u042f \u0412\u0425\u041e\u0414\u0410:")
rows = [
    ("admin",          "admin123", "ADMIN",       "\u0410\u043b\u0435\u043a\u0441\u0430\u043d\u0434\u0440 \u041f\u043e\u043f\u043e\u0432"),
    ("org_ivanova",    "org123",   "ORGANIZER",   "\u0415\u043a\u0430\u0442\u0435\u0440\u0438\u043d\u0430 \u0418\u0432\u0430\u043d\u043e\u0432\u0430"),
    ("org_petrov",     "org123",   "ORGANIZER",   "\u0414\u043c\u0438\u0442\u0440\u0438\u0439 \u041f\u0435\u0442\u0440\u043e\u0432"),
    ("smirnov_alex",   "user123",  "PARTICIPANT", "\u0410\u043b\u0435\u043a\u0441\u0435\u0439 \u0421\u043c\u0438\u0440\u043d\u043e\u0432"),
    ("kozlova_maria",  "user123",  "PARTICIPANT", "\u041c\u0430\u0440\u0438\u044f \u041a\u043e\u0437\u043b\u043e\u0432\u0430"),
    ("fedorova_anna",  "user123",  "PARTICIPANT", "\u0410\u043d\u043d\u0430 \u0424\u0451\u0434\u043e\u0440\u043e\u0432\u0430"),
    ("nikitin_igor",   "user123",  "PARTICIPANT", "\u0418\u0433\u043e\u0440\u044c \u041d\u0438\u043a\u0438\u0442\u0438\u043d"),
    ("sorokina_kate",  "user123",  "PARTICIPANT", "\u0415\u043a\u0430\u0442\u0435\u0440\u0438\u043d\u0430 \u0421\u043e\u0440\u043e\u043a\u0438\u043d\u0430"),
    ("morozov_pavel",  "user123",  "PARTICIPANT", "\u041f\u0430\u0432\u0435\u043b \u041c\u043e\u0440\u043e\u0437\u043e\u0432"),
    ("volkova_elena",  "user123",  "PARTICIPANT", "\u0415\u043b\u0435\u043d\u0430 \u0412\u043e\u043b\u043a\u043e\u0432\u0430"),
    ("observer_hr",    "obs123",   "OBSERVER",    "\u041d\u0430\u0442\u0430\u043b\u044c\u044f \u0421\u0435\u0440\u0433\u0435\u0435\u0432\u0430"),
]
for username, pwd, role, name in rows:
    print(f"  {username:<18} / {pwd:<10} \u2014 {role:<12} ({name})")
print()
print("\u0422\u041e\u041f-3 \u0420\u0415\u0419\u0422\u0418\u041d\u0413\u0410:")
for snap in RatingSnapshot.objects.order_by("rank")[:3]:
    print(f"  #{snap.rank}  {snap.user.get_full_name():<22}  \u041e\u0431\u0449.: {snap.common_rating}  IT: {snap.rating_it}  \u0421\u043e\u0446.: {snap.rating_social}  \u041c\u0435\u0434.: {snap.rating_media}")
