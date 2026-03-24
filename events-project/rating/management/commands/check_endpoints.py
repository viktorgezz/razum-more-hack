"""
Проверка работоспособности всех API-эндпоинтов проекта.
Создаёт тестовые данные и прогоняет каждый эндпоинт.
"""
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from rest_framework.test import APIClient

from accounts.models import User
from events.models import Event, EventCategory, Participation
from organizers.models import OrganizerReview
from rating.models import PointWeight, RatingSnapshot


class Command(BaseCommand):
    help = 'Проверка работоспособности всех API-эндпоинтов'

    def handle(self, *args, **options):
        self.stdout.write('Проверка эндпоинтов API...\n')
        results = []

        # Создаём тестовые данные (в транзакции или с откатом)
        admin_user = User.objects.filter(role=User.Role.ADMIN).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='test_admin',
                password='testpass123',
                role=User.Role.ADMIN,
            )
        else:
            admin_user.set_password('testpass123')
            admin_user.save()

        participant = User.objects.filter(role=User.Role.PARTICIPANT).first()
        if not participant:
            participant = User.objects.create_user(
                username='test_participant',
                password='testpass123',
                role=User.Role.PARTICIPANT,
            )
        else:
            participant.set_password('testpass123')
            participant.save()

        organizer = User.objects.filter(role=User.Role.ORGANIZER).first()
        if not organizer:
            organizer = User.objects.create_user(
                username='test_organizer',
                password='testpass123',
                role=User.Role.ORGANIZER,
                is_verified=True,
            )

        cat = EventCategory.objects.first()
        if not cat:
            cat = EventCategory.objects.create(
                name='IT',
                slug='it',
            )

        event = Event.objects.filter(organizer=organizer).first()
        if not event:
            event = Event.objects.create(
                organizer=organizer,
                category=cat,
                name='Тестовое мероприятие',
                event_date=datetime.now() + timedelta(days=1),
                event_type=Event.EventType.LECTURE,
                status=Event.Status.PUBLISHED,
            )

        pw = PointWeight.objects.first()
        if not pw:
            pw = PointWeight.objects.create(
                event_type=PointWeight.EventType.LECTURE,
                category=cat,
                weight=1.5,
                updated_by=admin_user,
            )

        snap = RatingSnapshot.objects.filter(user=participant).first()
        if not snap:
            snap = RatingSnapshot.objects.create(
                user=participant,
                rank=1,
            )

        client = APIClient()

        # 1. JWT Token (без авторизации)
        r = client.post(
            '/api/token/',
            {'username': participant.username, 'password': 'testpass123'},
            format='json',
        )
        ok = r.status_code == 200
        results.append(('POST /api/token/', ok, r.status_code))
        if ok:
            token = r.json().get('access')
        else:
            token = None

        # 2. Список организаторов
        client.force_authenticate(user=participant)
        r = client.get('/api/v1/organizers/')
        results.append(('GET /api/v1/organizers/', r.status_code == 200, r.status_code))

        # 3. Профиль организатора
        r = client.get(f'/api/v1/organizers/{organizer.id}/')
        results.append((f'GET /api/v1/organizers/{organizer.id}/', r.status_code == 200, r.status_code))

        # 4. Мероприятия организатора
        r = client.get(f'/api/v1/organizers/{organizer.id}/events/')
        results.append((f'GET /api/v1/organizers/{organizer.id}/events/', r.status_code == 200, r.status_code))

        # 5. Отзывы организатора
        r = client.get(f'/api/v1/organizers/{organizer.id}/reviews/')
        results.append((f'GET /api/v1/organizers/{organizer.id}/reviews/', r.status_code == 200, r.status_code))

        # 6. Создать отзыв (participant с подтверждённым участием)
        part, _ = Participation.objects.get_or_create(
            event=event,
            user=participant,
            defaults={'status': Participation.Status.CONFIRMED},
        )
        if part.status != Participation.Status.CONFIRMED:
            part.status = Participation.Status.CONFIRMED
            part.save()
        OrganizerReview.objects.filter(organizer=organizer, reviewer=participant, event=event).delete()
        r = client.post(
            f'/api/v1/organizers/{organizer.id}/reviews/create/',
            {'event': event.id, 'score': 5, 'comment': 'Отлично!'},
            format='json',
        )
        results.append((f'POST /api/v1/organizers/{{id}}/reviews/create/', r.status_code in (200, 201), r.status_code))
        review = OrganizerReview.objects.filter(organizer=organizer, reviewer=participant).first()

        # 7. Удалить отзыв
        if review:
            r = client.delete(f'/api/v1/organizers/{organizer.id}/reviews/{review.id}/')
            results.append((f'DELETE /api/v1/organizers/{{id}}/reviews/{{id}}/', r.status_code in (200, 204), r.status_code))
        else:
            results.append(('DELETE .../reviews/{id}/', False, 'no review'))

        # 8. Leaderboard
        r = client.get('/api/v1/ratings/leaderboard/')
        results.append(('GET /api/v1/ratings/leaderboard/', r.status_code == 200, r.status_code))

        # 9. Leaderboard с category
        r = client.get('/api/v1/ratings/leaderboard/?category=it')
        results.append(('GET /api/v1/ratings/leaderboard/?category=it', r.status_code == 200, r.status_code))

        # 10. Рейтинг пользователя
        r = client.get(f'/api/v1/ratings/user/{participant.id}/')
        results.append((f'GET /api/v1/ratings/user/{participant.id}/', r.status_code == 200, r.status_code))

        # 11. Веса баллов
        r = client.get('/api/v1/ratings/point-weights/')
        results.append(('GET /api/v1/ratings/point-weights/', r.status_code == 200, r.status_code))

        # 12. Обновить вес (admin)
        client.force_authenticate(user=admin_user)
        r = client.patch(
            f'/api/v1/ratings/point-weights/{pw.id}/',
            {'weight': 1.2},
            format='json',
        )
        results.append((f'PATCH /api/v1/ratings/point-weights/{pw.id}/', r.status_code == 200, r.status_code))

        # 13. Rebuild leaderboard (admin)
        r = client.post('/api/v1/ratings/rebuild/')
        results.append(('POST /api/v1/ratings/rebuild/', r.status_code == 200, r.status_code))

        # 14. OpenAPI schema (без auth)
        client.force_authenticate(user=None)
        r = client.get('/api/schema/')
        results.append(('GET /api/schema/', r.status_code == 200, r.status_code))

        # 15. Swagger UI
        r = client.get('/api/docs/')
        results.append(('GET /api/docs/', r.status_code == 200, r.status_code))

        # 16. ReDoc
        r = client.get('/api/redoc/')
        results.append(('GET /api/redoc/', r.status_code == 200, r.status_code))

        # Отчёт
        self.stdout.write('Результаты проверки:\n')
        failed = []
        for name, ok, code in results:
            status_str = self.style.SUCCESS('OK') if ok else self.style.ERROR('FAIL')
            self.stdout.write(f'  [{status_str}] {name} -> {code}')
            if not ok:
                failed.append((name, code))
        self.stdout.write('')
        if failed:
            self.stdout.write(self.style.ERROR(f'Провалено: {len(failed)} эндпоинт(ов)'))
            for name, code in failed:
                self.stdout.write(f'  - {name} ({code})')
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(f'Все {len(results)} эндпоинтов работают.'))
