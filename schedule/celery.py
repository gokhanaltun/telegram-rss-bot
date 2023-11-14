from celery import Celery
from celery.schedules import crontab

app = Celery("rssBot",
             broker="redis://localhost:6379/0",
             backend="redis://localhost:6379/0",
             include=["tasks"])

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Istanbul',
    enable_utc=True,
)

app.conf.worker_concurrency = 2

app.conf.beat_schedule = {
    'my-scheduled-task': {
        'task': "tasks.check_and_process_rss_feed_every_minutes",
        'schedule': crontab(minute="*/1"),
    },
}
