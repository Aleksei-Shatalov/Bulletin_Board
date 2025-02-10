import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bulletin_Board.settings')

app = Celery('Bulletin_Board')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

#app.conf.beat_schedule = {
    #'print_every_5_seconds': {
        #'task': 'board.tasks.printer',
        #'schedule': 5,
        #'args': (5,),
    #},
#}

app.conf.beat_schedule = {
    'send_weekly_newsletters_every_monday_8am': {
        'task': 'news_app.tasks.send_weekly_newsletters_task',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}