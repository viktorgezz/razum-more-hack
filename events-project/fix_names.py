# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'events-project'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django; django.setup()

from accounts.models import User

updates = [
    ('ivanova_elena',  '\u0415\u043b\u0435\u043d\u0430',   '\u0418\u0432\u0430\u043d\u043e\u0432\u0430'),
    ('petrov_dmitry',  '\u0414\u043c\u0438\u0442\u0440\u0438\u0439', '\u041f\u0435\u0442\u0440\u043e\u0432'),
    ('smirnov_alex',   '\u0410\u043b\u0435\u043a\u0441\u0435\u0439', '\u0421\u043c\u0438\u0440\u043d\u043e\u0432'),
    ('kozlova_maria',  '\u041c\u0430\u0440\u0438\u044f',   '\u041a\u043e\u0437\u043b\u043e\u0432\u0430'),
    ('novikov_ivan',   '\u0418\u0432\u0430\u043d',         '\u041d\u043e\u0432\u0438\u043a\u043e\u0432'),
    ('fedorova_anna',  '\u0410\u043d\u043d\u0430',         '\u0424\u0451\u0434\u043e\u0440\u043e\u0432\u0430'),
    ('zaitsev_nikita', '\u041d\u0438\u043a\u0438\u0442\u0430', '\u0417\u0430\u0439\u0446\u0435\u0432'),
    ('observer_hr',    '\u041a\u0430\u0434\u0440\u043e\u0432\u0430\u044f', '\u0421\u043b\u0443\u0436\u0431\u0430'),
]

for username, first, last in updates:
    count = User.objects.filter(username=username).update(first_name=first, last_name=last)
    print('Updated {} -> {} {}'.format(username, first.encode('utf-8'), last.encode('utf-8')))

# Also update event names to Russian
from events.models import Event, EventCategory

EventCategory.objects.filter(slug='it').update(name='\u0418\u0422')
EventCategory.objects.filter(slug='social').update(name='\u0421\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435')
EventCategory.objects.filter(slug='media').update(name='\u041c\u0435\u0434\u0438\u0430')

names_map = {
    'Hakaton Tsifrovoy region': '\u0425\u0430\u043a\u0430\u0442\u043e\u043d \xab\u0426\u0438\u0444\u0440\u043e\u0432\u043e\u0439 \u0440\u0435\u0433\u0438\u043e\u043d\xbb',
    'Lektsiya: kariera v IT': '\u041b\u0435\u043a\u0446\u0438\u044f: \u043a\u0430\u0440\u044c\u0435\u0440\u0430 \u0432 IT',
    'Forum molodykh liderov': '\u0424\u043e\u0440\u0443\u043c \u043c\u043e\u043b\u043e\u0434\u044b\u0445 \u043b\u0438\u0434\u0435\u0440\u043e\u0432',
    'Volonterskaya aktsiya Chisty gorod': '\u0412\u043e\u043b\u043e\u043d\u0442\u0451\u0440\u0441\u043a\u0430\u044f \u0430\u043a\u0446\u0438\u044f \xab\u0427\u0438\u0441\u0442\u044b\u0439 \u0433\u043e\u0440\u043e\u0434\xbb',
    'Mediashkola molodezhnogo parlamenta': '\u041c\u0435\u0434\u0438\u0430\u0448\u043a\u043e\u043b\u0430 \u043c\u043e\u043b\u043e\u0434\u0451\u0436\u043d\u043e\u0433\u043e \u043f\u0430\u0440\u043b\u0430\u043c\u0435\u043d\u0442\u0430',
    'Hakaton GovTech 2025': '\u0425\u0430\u043a\u0430\u0442\u043e\u043d \xabGovTech 2025\xbb',
    'Vorkshop: sozdanie podkastov': '\u0412\u043e\u0440\u043a\u0448\u043e\u043f: \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u043e\u0434\u043a\u0430\u0441\u0442\u043e\u0432',
    'IT-forum Budushchee za nami': 'IT-\u0444\u043e\u0440\u0443\u043c \xab\u0411\u0443\u0434\u0443\u0449\u0435\u0435 \u0437\u0430 \u043d\u0430\u043c\u0438\xbb',
}
for old_name, new_name in names_map.items():
    Event.objects.filter(name=old_name).update(name=new_name)
    print('Event: {} -> {}'.format(old_name, new_name.encode('utf-8')))

print('Done.')
