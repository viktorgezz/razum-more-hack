# -*- coding: utf-8 -*-
import django
import os
import sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, 'events-project'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.models import User
from events.models import Event, EventCategory, Prize, Participation
from organizers.models import OrganizerReview
from rating.services import rebuild_leaderboard

# --- Категории ---
cat_it, _     = EventCategory.objects.update_or_create(
    slug='it',     defaults={'name': 'IT',                         'description': 'IT-meropriyatiya'})
cat_social, _ = EventCategory.objects.update_or_create(
    slug='social', defaults={'name': 'Sotsialnoe proektirovanie',  'description': 'Sotsialnye initsiativy'})
cat_media, _  = EventCategory.objects.update_or_create(
    slug='media',  defaults={'name': 'Media',                      'description': 'Media i kommunikatsii'})
print('Kategorii: {}'.format(EventCategory.objects.count()))

# --- Polzovateli ---
def make_user(username, first, last, role, email, city='Moskva', password='test1234'):
    u, created = User.objects.get_or_create(username=username, defaults=dict(
        first_name=first, last_name=last, email=email,
        role=role, city=city, is_verified=(role == 'ORGANIZER'),
    ))
    if created:
        u.set_password(password)
        u.save()
    return u

org1 = make_user('ivanova_elena',  'Elena',    'Ivanova',   'ORGANIZER',   'ivanova@test.com',  'Moskva')
org2 = make_user('petrov_dmitry',  'Dmitry',   'Petrov',    'ORGANIZER',   'petrov@test.com',   'Sankt-Peterburg')
p1   = make_user('smirnov_alex',   'Alexey',   'Smirnov',   'PARTICIPANT', 'smirnov@test.com',  'Kazan')
p2   = make_user('kozlova_maria',  'Maria',    'Kozlova',   'PARTICIPANT', 'kozlova@test.com',  'Moskva')
p3   = make_user('novikov_ivan',   'Ivan',     'Novikov',   'PARTICIPANT', 'novikov@test.com',  'Ekaterinburg')
p4   = make_user('fedorova_anna',  'Anna',     'Fedorova',  'PARTICIPANT', 'fedorova@test.com', 'Moskva')
p5   = make_user('zaitsev_nikita', 'Nikita',   'Zaitsev',   'PARTICIPANT', 'zaitsev@test.com',  'Novosibirsk')
obs  = make_user('observer_hr',    'HR',       'Observer',  'OBSERVER',    'hr@test.com',       'Moskva')
print('Polzovatelei: {}'.format(User.objects.count()))

# --- Meropriyatiya ---
now = timezone.now()

def make_event(organizer, name, etype, category, status, diff, points, days_ago, desc='', max_p=100):
    e, _ = Event.objects.get_or_create(name=name, defaults=dict(
        organizer=organizer, category=category,
        description=desc or name,
        event_date=now - timedelta(days=days_ago),
        event_type=etype,
        difficulty_coef=Decimal(str(diff)),
        base_points=points,
        max_participants=max_p,
        status=status,
    ))
    return e

e1 = make_event(org1, 'Hakaton Tsifrovoy region',      'HACKATHON', cat_it,     'COMPLETED', 2.0, 100, 60,
                'Razrabotka IT-resheniy dlya regionalnogo upravleniya')
e2 = make_event(org1, 'Lektsiya: kariera v IT',        'LECTURE',   cat_it,     'COMPLETED', 1.0,  30, 40)
e3 = make_event(org2, 'Forum molodykh liderov',        'FORUM',     cat_social, 'COMPLETED', 1.5,  60, 90,
                'Ezhegodnyy forum dlya razvitiya liderskikh kachestv')
e4 = make_event(org2, 'Volonterskaya aktsiya Chisty gorod', 'VOLUNTEER', cat_social, 'COMPLETED', 1.0, 20, 30)
e5 = make_event(org1, 'Mediashkola molodezhnogo parlamenta', 'FORUM', cat_media, 'COMPLETED', 1.5, 50, 20,
                'Obuchenie osnovam zhurnalistiki i SMM')
e6 = make_event(org2, 'Hakaton GovTech 2025',          'HACKATHON', cat_it,     'COMPLETED', 2.5,  80, 15)
e7 = make_event(org1, 'Vorkshop: sozdanie podkastov',  'LECTURE',   cat_media,  'PUBLISHED', 1.0,  25, -7,
                'Prakticheskiy vorkshop po sozdaniyu audiokontenta')
e8 = make_event(org2, 'IT-forum Budushchee za nami',   'FORUM',     cat_it,     'ONGOING',   1.8,  70,  0)
print('Meropriyatiy: {}'.format(Event.objects.count()))

# --- Prizy ---
prizes_data = [
    (e1, [('Stazhirovka Sber', 'INTERNSHIP', 1), ('Merch hakatona', 'MERCH', 10)]),
    (e3, [('Bilety na konferentsiyu', 'TICKETS', 5), ('Grant 50000', 'GRANT', 3)]),
    (e5, [('Vstrecha s zhurnalistom', 'MEETING', 1), ('Merch mediashkoly', 'MERCH', 20)]),
    (e6, [('Grant na proekt 100000', 'GRANT', 2), ('Stazhirovka', 'INTERNSHIP', 2)]),
]
for event, plist in prizes_data:
    for pname, ptype, qty in plist:
        Prize.objects.get_or_create(event=event, name=pname, defaults=dict(
            description=pname, prize_type=ptype, quantity=qty))
print('Prizov: {}'.format(Prize.objects.count()))

# --- Uchastiya ---
participations = [
    (p1, e1, 'CONFIRMED', 100),
    (p1, e2, 'CONFIRMED',  30),
    (p1, e3, 'CONFIRMED',  60),
    (p1, e6, 'CONFIRMED',  80),
    (p2, e1, 'CONFIRMED',  80),
    (p2, e3, 'CONFIRMED',  60),
    (p2, e5, 'CONFIRMED',  50),
    (p2, e4, 'CONFIRMED',  20),
    (p3, e3, 'CONFIRMED',  60),
    (p3, e4, 'CONFIRMED',  20),
    (p3, e6, 'CONFIRMED',  70),
    (p4, e1, 'CONFIRMED',  90),
    (p4, e2, 'CONFIRMED',  30),
    (p4, e5, 'CONFIRMED',  50),
    (p5, e2, 'CONFIRMED',  25),
    (p5, e5, 'CONFIRMED',  40),
    (p1, e7, 'REGISTERED',  0),
    (p2, e8, 'REGISTERED',  0),
    (p3, e7, 'CHECKED_IN',  0),
    (p4, e8, 'REGISTERED',  0),
]
for user, event, status, pts in participations:
    Participation.objects.get_or_create(user=user, event=event, defaults=dict(
        status=status, points_awarded=pts,
        qr_token='qr-{}-{}'.format(user.username, event.id),
    ))
print('Uchastiy: {}'.format(Participation.objects.count()))

# --- Otzyvy ---
reviews = [
    (p1, org1, e1, 5, 'Otlichnyy organizator! Vse chetko.'),
    (p2, org1, e1, 4, 'Khoroshiy hakaton, no reglament zatayanulsya.'),
    (p4, org1, e1, 5, 'Luchshiy hakaton, spasibo!'),
    (p1, org2, e3, 4, 'Forum ochen poleznyy.'),
    (p2, org2, e3, 5, 'Velikolepnaya organizatsiya.'),
    (p3, org2, e3, 3, 'Khorosho, no khotelosb bolshe netvorkinga.'),
    (p3, org2, e6, 5, 'Krutoy hakaton, zadachi realno slozhye.'),
]
for reviewer, organizer, event, score, comment in reviews:
    OrganizerReview.objects.get_or_create(reviewer=reviewer, event=event, defaults=dict(
        organizer=organizer, score=score, comment=comment))
print('Otzyvov: {}'.format(OrganizerReview.objects.count()))

# --- Pererashet reytinga ---
rebuild_leaderboard()
from rating.models import RatingSnapshot
print('Snapshotov reytinga: {}'.format(RatingSnapshot.objects.count()))
for snap in RatingSnapshot.objects.order_by('rank'):
    u = snap.user
    print('  #{} {} {} -- obshchiy: {}  IT: {}  Social: {}  Media: {}'.format(
        snap.rank, u.first_name, u.last_name,
        snap.common_rating, snap.rating_it, snap.rating_social, snap.rating_media))

print('\nGotovo! Baza zapolnena.')
